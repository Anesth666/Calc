# main.py
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.slider import MDSlider
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import re

# Настройка окна для разработки
#Window.size = (360, 640)

class DrugData:
    """Класс с информацией о препаратах"""
    
    DRUGS = {
        'norepinephrine': {
            'id': 'norepinephrine',
            'name': 'Норэпинефрин',
            'short_name': 'Норэп',
            'color': '#FF6B6B',
            'color_light': '#FF6B6B20',
            'color_medium': '#FF6B6B40',
            'default_ampoule': '4 мг',
            'info': '4 мг на 200 мл',
            'standard_dose': '0.05-0.5 мкг/кг/мин',
            'default_amount': '4',
            'default_volume': '200',
            'max_rate': 30,
            'icon': 'heart-pulse'
        },
        'dobutamine': {
            'id': 'dobutamine',
            'name': 'Добутамин',
            'short_name': 'Добут',
            'color': '#4ECDC4',
            'color_light': '#4ECDC420',
            'color_medium': '#4ECDC440',
            'default_ampoule': '250 мг',
            'info': '250 мг на 50 мл',
            'standard_dose': '2-20 мкг/кг/мин',
            'default_amount': '250',
            'default_volume': '50',
            'max_rate': 50,
            'icon': 'heart'
        },
        'dopamine': {
            'id': 'dopamine',
            'name': 'Допамин',
            'short_name': 'Допам',
            'color': '#45B7D1',
            'color_light': '#45B7D120',
            'color_medium': '#45B7D140',
            'default_ampoule': '200 мг',
            'info': '200 мг на 50 мл',
            'standard_dose': '2-20 мкг/кг/мин',
            'default_amount': '200',
            'default_volume': '50',
            'max_rate': 40,
            'icon': 'brain'
        },
        'epinephrine': {
            'id': 'epinephrine',
            'name': 'Эпинефрин',
            'short_name': 'Эпи',
            'color': '#96CEB4',
            'color_light': '#96CEB420',
            'color_medium': '#96CEB440',
            'default_ampoule': '1 мг',
            'info': '1 мг на 50 мл',
            'standard_dose': '0.01-0.1 мкг/кг/мин',
            'default_amount': '1',
            'default_volume': '50',
            'max_rate': 20,
            'icon': 'lightning-bolt'
        }
    }
    
    @staticmethod
    def calculate_rate(drug_mg, volume_ml, weight_kg, dose_mcg_kg_min):
        """Расчет скорости инфузии в мл/ч"""
        try:
            drug_mcg = float(drug_mg) * 1000
            concentration = drug_mcg / float(volume_ml)
            dose_mcg_min = float(weight_kg) * float(dose_mcg_kg_min)
            rate_ml_h = (dose_mcg_min * 60) / concentration
            return round(rate_ml_h, 1)
        except (ZeroDivisionError, ValueError, TypeError):
            return 0
    
    @staticmethod
    def calculate_dose_from_rate(drug_mg, volume_ml, weight_kg, rate_ml_h):
        """Расчет дозы в мкг/кг/мин из скорости инфузии"""
        try:
            drug_mcg = float(drug_mg) * 1000
            concentration = drug_mcg / float(volume_ml)
            dose_mcg_min = (rate_ml_h * concentration) / 60
            dose_mcg_kg_min = dose_mcg_min / float(weight_kg)
            return round(dose_mcg_kg_min, 2)
        except (ZeroDivisionError, ValueError, TypeError):
            return 0

class DrugCard(MDCard):
    """Карточка препарата на главном экране - нажатие на всю карточку"""
    
    def __init__(self, drug_id, drug_info, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.drug_id = drug_id
        self.drug_info = drug_info
        self.main_screen = main_screen
        self.selected = False
        
        # Настройки карточки
        self.orientation = "horizontal"
        self.padding = dp(10)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(70)
        self.radius = dp(8)
        self.elevation = 2
        self.md_bg_color = get_color_from_hex(drug_info['color_light'])
        
        # Делаем всю карточку кликабельной
        self.ripple_behavior = True
        self.bind(on_release=self.on_card_press)
        
        # Иконка препарата
        icon = MDIconButton(
            icon=drug_info['icon'],
            theme_text_color='Custom',
            text_color=get_color_from_hex(drug_info['color']),
            disabled=True,
            size_hint_x=0.15
        )
        self.add_widget(icon)
        
        # Информация о препарате
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        name_label = MDLabel(
            text=drug_info['name'],
            font_style='Subtitle2',
            size_hint_y=0.5,
            theme_text_color='Custom',
            text_color=get_color_from_hex(drug_info['color'])
        )
        info_layout.add_widget(name_label)
        
        info_label = MDLabel(
            text=drug_info['info'],
            font_style='Caption',
            size_hint_y=0.5,
            theme_text_color='Secondary'
        )
        info_layout.add_widget(info_label)
        
        self.add_widget(info_layout)
        
        # Индикатор выбора (только для визуальной обратной связи)
        self.status_icon = MDIconButton(
            icon='checkbox-blank-circle-outline',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#888888'),
            disabled=True,
            size_hint_x=0.15
        )
        self.add_widget(self.status_icon)
    
    def on_card_press(self, instance):
        """Обработка нажатия на карточку"""
        if self.main_screen:
            self.main_screen.select_drug(self.drug_id, self)
    
    def set_selected(self, selected):
        """Установка состояния выбора"""
        self.selected = selected
        if selected:
            self.status_icon.icon = 'checkbox-marked-circle'
            self.status_icon.text_color = get_color_from_hex(self.drug_info['color'])
            self.md_bg_color = get_color_from_hex(self.drug_info['color_medium'])
            self.elevation = 4
        else:
            self.status_icon.icon = 'checkbox-blank-circle-outline'
            self.status_icon.text_color = get_color_from_hex('#888888')
            self.md_bg_color = get_color_from_hex(self.drug_info['color_light'])
            self.elevation = 2

class MainScreen(MDScreen):
    """Главный экран с весом и списком препаратов"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.selected_drug = None
        self.drug_cards = {}
        self.dialog = None
        
        # Основной контейнер
        layout = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        
        # Заголовок
        title = MDLabel(
            text='Калькулятор инфузии',
            font_style='H5',
            size_hint_y=None,
            height=dp(50),
            halign='center',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#4CAF50')
        )
        layout.add_widget(title)
        
        # Карточка ввода веса
        weight_card = MDCard(
            orientation='horizontal',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(70),
            radius=[dp(10)],
            elevation=2
        )
        
        # Иконка веса
        weight_icon = MDIconButton(
            icon='human',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#4CAF50'),
            disabled=True,
            size_hint_x=0.15
        )
        weight_card.add_widget(weight_icon)
        
        # Поле ввода веса
        self.weight_field = MDTextField(
            hint_text='Вес (кг)',
            mode='fill',
            size_hint_x=0.6,
            input_filter='float',
            input_type='number'
        )
        self.weight_field.bind(text=self.on_weight_input)
        weight_card.add_widget(self.weight_field)
        
        # Индикатор статуса
        self.status_icon = MDIconButton(
            icon='checkbox-blank-circle-outline',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#888888'),
            disabled=True,
            size_hint_x=0.15
        )
        weight_card.add_widget(self.status_icon)
        
        layout.add_widget(weight_card)
        
        # Список препаратов
        drugs_label = MDLabel(
            text='Выберите препарат:',
            font_style='Subtitle1',
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(drugs_label)
        
        # Контейнер для карточек препаратов
        self.drugs_container = MDBoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.drugs_container.bind(minimum_height=self.drugs_container.setter('height'))
        
        # Создаем карточки для всех препаратов
        for drug_id, drug_info in DrugData.DRUGS.items():
            card = DrugCard(drug_id, drug_info, self)
            self.drug_cards[drug_id] = card
            self.drugs_container.add_widget(card)
        
        layout.add_widget(self.drugs_container)
        
        self.add_widget(layout)
    
    def on_weight_input(self, instance, text):
        """Обработка ввода веса"""
        if text and text.strip() and text != '0':
            try:
                weight = float(text)
                if 1 <= weight <= 300:
                    self.manager.weight = weight
                    self.status_icon.icon = 'check-circle'
                    self.status_icon.text_color = get_color_from_hex('#4CAF50')
                else:
                    self.status_icon.icon = 'close-circle'
                    self.status_icon.text_color = get_color_from_hex('#FF4444')
                    self.manager.weight = None
            except ValueError:
                self.status_icon.icon = 'close-circle'
                self.status_icon.text_color = get_color_from_hex('#FF4444')
                self.manager.weight = None
        else:
            self.status_icon.icon = 'checkbox-blank-circle-outline'
            self.status_icon.text_color = get_color_from_hex('#888888')
            self.manager.weight = None
    
    def select_drug(self, drug_id, card):
        """Выбор препарата и переход к расчету"""
        
        # Проверяем, введен ли вес
        if not self.manager.weight:
            self.show_weight_error()
            return
        
        # Снимаем выделение со всех карточек
        for d_id, d_card in self.drug_cards.items():
            d_card.set_selected(d_id == drug_id)
        
        self.selected_drug = drug_id
        self.manager.selected_drug = drug_id
        
        # Переходим к экрану расчета
        self.manager.current = 'calculation'
    
    def show_weight_error(self):
        """Показывает диалог об ошибке - вес не введен"""
        if not self.dialog:
            self.dialog = MDDialog(
                title='Вес не указан',
                text='Пожалуйста, введите вес пациента перед выбором препарата',
                buttons=[
                    MDFlatButton(
                        text='OK',
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.open()

class CalculationScreen(MDScreen):
    """Экран расчета с слайдером"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'calculation'
        
        layout = MDBoxLayout(orientation='vertical')
        
        # Верхняя панель
        toolbar = MDTopAppBar(
            title='Расчет',
            elevation=2,
            left_action_items=[['arrow-left', lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Основной контент
        scroll = ScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Карточка препарата
        drug_card = MDCard(
            orientation='horizontal',
            padding=dp(10),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(60),
            radius=[dp(8)],
            elevation=1
        )
        
        self.drug_icon = MDIconButton(
            icon='pill',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#4CAF50'),
            disabled=True,
            size_hint_x=0.15
        )
        drug_card.add_widget(self.drug_icon)
        
        self.drug_name = MDLabel(
            text='',
            font_style='Subtitle1',
            size_hint_x=0.5
        )
        drug_card.add_widget(self.drug_name)
        
        self.weight_display = MDLabel(
            text='',
            font_style='Caption',
            halign='right',
            size_hint_x=0.35,
            theme_text_color='Secondary'
        )
        drug_card.add_widget(self.weight_display)
        
        content.add_widget(drug_card)
        
        # Карточка параметров разведения
        params_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(120),
            radius=[dp(8)],
            elevation=1
        )
        
        params_title = MDLabel(
            text='Параметры разведения:',
            font_style='Caption',
            size_hint_y=None,
            height=dp(20),
            theme_text_color='Secondary'
        )
        params_card.add_widget(params_title)
        
        # Поля ввода в одну строку
        inputs_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(48))
        
        self.drug_amount = MDTextField(
            hint_text='мг',
            mode='fill',
            size_hint_x=0.5,
            input_filter='float',
            input_type='number'
        )
        self.drug_amount.bind(text=self.on_input_change)
        inputs_layout.add_widget(self.drug_amount)
        
        self.volume = MDTextField(
            hint_text='мл',
            mode='fill',
            size_hint_x=0.5,
            input_filter='float',
            input_type='number'
        )
        self.volume.bind(text=self.on_input_change)
        inputs_layout.add_widget(self.volume)
        
        params_card.add_widget(inputs_layout)
        
        # Концентрация
        self.concentration_label = MDLabel(
            text='-- мкг/мл',
            font_style='Caption',
            size_hint_y=None,
            height=dp(20),
            halign='right',
            theme_text_color='Secondary'
        )
        params_card.add_widget(self.concentration_label)
        
        content.add_widget(params_card)
        
        # Карточка с результатом
        result_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180),
            radius=[dp(12)],
            elevation=3,
            md_bg_color=get_color_from_hex('#1E3A2F')
        )
        
        result_title = MDLabel(
            text='СКОРОСТЬ ИНФУЗИИ',
            font_style='Caption',
            halign='center',
            size_hint_y=None,
            height=dp(20),
            theme_text_color='Custom',
            text_color=get_color_from_hex('#4CAF50')
        )
        result_card.add_widget(result_title)
        
        # Отображение скорости крупно
        self.rate_display = MDLabel(
            text='0.0 мл/ч',
            font_style='H3',
            halign='center',
            size_hint_y=None,
            height=dp(60),
            theme_text_color='Custom',
            text_color=get_color_from_hex('#FFFFFF')
        )
        result_card.add_widget(self.rate_display)
        
        # Соответствующая доза
        self.dose_display = MDLabel(
            text='0.00 мкг/кг/мин',
            font_style='Subtitle1',
            halign='center',
            size_hint_y=None,
            height=dp(30),
            theme_text_color='Custom',
            text_color=get_color_from_hex('#4CAF50')
        )
        result_card.add_widget(self.dose_display)
        
        content.add_widget(result_card)
        
        # Карточка с слайдером
        slider_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(130),
            radius=[dp(8)],
            elevation=1
        )
        
        slider_label = MDLabel(
            text='Регулировка скорости:',
            font_style='Caption',
            size_hint_y=None,
            height=dp(20),
            theme_text_color='Secondary'
        )
        slider_card.add_widget(slider_label)
        
        # Слайдер с шагом 0.1
        self.rate_slider = MDSlider(
            min=0,
            max=50,
            value=0,
            step=0.1,
            size_hint_y=None,
            height=dp(40)
        )
        self.rate_slider.bind(value=self.on_slider_change)
        slider_card.add_widget(self.rate_slider)
        
        # Отображение значения слайдера
        slider_value_layout = BoxLayout(orientation='horizontal', spacing=dp(20), size_hint_y=None, height=dp(40))
        
        decrease_btn = MDIconButton(
            icon='minus-circle',
            on_release=lambda x: self.adjust_rate(-0.1),
            theme_text_color='Custom',
            text_color=get_color_from_hex('#4CAF50'),
            icon_size=dp(24)
        )
        slider_value_layout.add_widget(decrease_btn)
        
        self.slider_value_label = MDLabel(
            text='0.0 мл/ч',
            halign='center',
            font_style='Subtitle2',
            size_hint_x=0.7
        )
        slider_value_layout.add_widget(self.slider_value_label)
        
        increase_btn = MDIconButton(
            icon='plus-circle',
            on_release=lambda x: self.adjust_rate(0.1),
            theme_text_color='Custom',
            text_color=get_color_from_hex('#4CAF50'),
            icon_size=dp(24)
        )
        slider_value_layout.add_widget(increase_btn)
        
        slider_card.add_widget(slider_value_layout)
        
        # Подсказка
        hint_label = MDLabel(
            text='Передвигайте слайдер или используйте кнопки +/-',
            font_style='Caption',
            size_hint_y=None,
            height=dp(20),
            halign='center',
            theme_text_color='Secondary'
        )
        slider_card.add_widget(hint_label)
        
        content.add_widget(slider_card)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        self.update_timer = None
    
    def on_enter(self):
        """Вызывается при входе на экран"""
        drug_id = self.manager.selected_drug
        drug_info = DrugData.DRUGS.get(drug_id, {})
        
        if drug_info:
            self.drug_icon.icon = drug_info.get('icon', 'pill')
            self.drug_name.text = drug_info.get('short_name', drug_info.get('name', ''))
            self.weight_display.text = f"{self.manager.weight} кг"
            
            # Устанавливаем значения по умолчанию
            self.drug_amount.text = drug_info.get('default_amount', '')
            self.volume.text = drug_info.get('default_volume', '')
            self.rate_slider.max = drug_info.get('max_rate', 50)
            self.rate_slider.value = 0
            
            # Обновляем отображение
            self.update_concentration()
            self.update_dose_from_rate()
    
    def on_input_change(self, instance, value):
        """Обработка изменения полей ввода"""
        self.update_concentration()
        self.update_dose_from_rate()
    
    def update_concentration(self, *args):
        """Обновление отображения концентрации"""
        try:
            if self.drug_amount.text and self.volume.text:
                drug_mg = float(self.drug_amount.text)
                vol_ml = float(self.volume.text)
                if vol_ml > 0:
                    concentration = (drug_mg * 1000) / vol_ml
                    self.concentration_label.text = f'{round(concentration, 1)} мкг/мл'
                else:
                    self.concentration_label.text = '-- мкг/мл'
            else:
                self.concentration_label.text = '-- мкг/мл'
        except (ValueError, ZeroDivisionError):
            self.concentration_label.text = '-- мкг/мл'
    
    def on_slider_change(self, instance, value):
        """Обработка изменения слайдера"""
        display_value = round(value, 1)
        self.rate_display.text = f'{display_value:.1f} мл/ч'
        self.slider_value_label.text = f'{display_value:.1f} мл/ч'
        
        if self.update_timer:
            self.update_timer.cancel()
        
        self.update_timer = Clock.schedule_once(lambda dt: self.update_dose_from_rate(), 0.1)
    
    def adjust_rate(self, delta):
        """Изменение скорости на заданный шаг (0.1 мл/ч)"""
        new_value = self.rate_slider.value + delta
        new_value = round(new_value, 1)
        if self.rate_slider.min <= new_value <= self.rate_slider.max:
            self.rate_slider.value = new_value
    
    def update_dose_from_rate(self):
        """Обновление дозы на основе скорости"""
        try:
            if not all([self.drug_amount.text, self.volume.text, self.manager.weight]):
                self.dose_display.text = '-- мкг/кг/мин'
                return
            
            drug_mg = float(self.drug_amount.text)
            volume_ml = float(self.volume.text)
            rate = self.rate_slider.value
            
            if volume_ml <= 0:
                self.dose_display.text = '-- мкг/кг/мин'
                return
            
            dose = DrugData.calculate_dose_from_rate(drug_mg, volume_ml, self.manager.weight, rate)
            
            if dose > 0:
                self.dose_display.text = f'{dose:.2f} мкг/кг/мин'
            else:
                self.dose_display.text = '-- мкг/кг/мин'
                
        except (ValueError, ZeroDivisionError):
            self.dose_display.text = '-- мкг/кг/мин'
    
    def go_back(self):
        """Возврат на главный экран"""
        self.manager.current = 'main'

class MedCalcApp(MDApp):
    """Главный класс приложения"""
    
    def build(self):
        # Настройка темы
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.material_style = "M3"
        
        # Создаем менеджер экранов
        self.sm = MDScreenManager()
        
        # Добавляем экраны
        self.sm.add_widget(MainScreen())
        self.sm.add_widget(CalculationScreen())
        
        # Данные приложения
        self.sm.weight = None
        self.sm.selected_drug = None
        
        return self.sm
    
    def on_start(self):
        self.root.current = 'main'

if __name__ == "__main__":
    MedCalcApp().run()