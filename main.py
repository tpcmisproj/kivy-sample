import os
import sqlite3
import json
import requests
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField


class GasMenu(Screen):
    def change_screen(self, screen_name):
        self.manager.current = screen_name


class GasMenuH2Gas(Screen):
    def change_screen(self, screen_name):
        self.manager.current = screen_name


class MainMenu(Screen):
    def change_screen(self, screen_name):
        self.manager.current = screen_name


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.setup_ui()

    def setup_ui(self):
        layout = RelativeLayout()

        box_layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            adaptive_height=True,
            size_hint_x=0.8,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        box_layout.padding = dp(48)

        self.image = Image(
            source='tpc.jpg',
            size_hint=(None, None),
            size=(300, 200),
            pos_hint={"center_x": 0.5}
        )

        self.label_login = MDLabel(
            text="Please Log in using your HRIS Account", size_hint_y=None, height=dp(48))

        self.username = MDTextField(
            hint_text="Username", size_hint_y=None, height=dp(48))
        self.password = MDTextField(
            hint_text="Password", size_hint_y=None, height=dp(48), password=True)

        box_layout.add_widget(self.image)
        box_layout.add_widget(self.label_login)
        box_layout.add_widget(self.username)
        box_layout.add_widget(self.password)

        self.login_button = MDRaisedButton(
            text="Log In", on_release=self.on_login, size_hint_y=None, height=dp(48))
        box_layout.add_widget(self.login_button)

        layout.add_widget(box_layout)

        self.add_widget(layout)

    def on_login(self, *args):
        if self.is_internet_connected():
            response = self.log_in_function(
                self.username.text, self.password.text)
            if response['result'] is not False:
                self.logged_in_user_data = response['result']
                print(
                    f"==>> self.logged_in_user_data: {self.logged_in_user_data}")
                self.manager.current = 'menu'
            else:
                self.show_login_failure_dialog()
        else:

            self.log_in_local()

    def is_internet_connected(self):
        try:
            requests.get("http://www.google.com", timeout=3)
            return True
        except requests.ConnectionError:
            return False

    def log_in_local(self):

        local_data_file = "data.json"
        if os.path.exists(local_data_file):
            with open(local_data_file, "r") as file:
                data = json.load(file)
                for user_data in data.get("result", []):
                    if (
                        user_data.get("username") == self.username.text
                        and user_data.get("username") == self.username.text
                    ):
                        self.logged_in_user_data = user_data
                        print(
                            f"==>> self.logged_in_user_data: {self.logged_in_user_data}")
                        self.manager.current = 'menu'
                        return

                self.show_login_failure_dialog()
        else:
            self.show_login_failure_dialog()

    def log_in_function(self, username, password):
        url = f"http://hris.teamglac.com/api/users/login?u={username}&p={password}"
        response = requests.get(url).json()
        return response

    def show_login_failure_dialog(self):
        dialog = MDDialog(
            title="Login Failed",
            text="Invalid username or password. Please try again.",
            buttons=[MDRaisedButton(
                text="OK", on_release=lambda _: dialog.dismiss())]
        )
        dialog.open()

    def go_to_home(self):
        self.root.current = 'login'


class ContentNavigationDrawer(MDBoxLayout):
    pass


class Example(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_file("main.kv")

    def create_database(self):
        db_file = 'gas_data.db'
        if not os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE ShiftData (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Date TEXT,
                    Shift TEXT,
                    Temperature TEXT,
                    Nitrogen TEXT,
                    Pressure TEXT,
                    NitrogenCylinderPressure TEXT,
                    PrimaryPressureGaugeBH2 TEXT,
                    Time TEXT,
                    PrimaryPressureGaugePallet TEXT,
                    Remarks TEXT,
                    SecondaryPressureGaugeBH2 TEXT
                )
            ''')

            conn.commit()
            conn.close()

    def build(self):
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Orange"
        self.menu_items = [
            {
                "viewclass": "OneLineListItem",
                "icon": "android",
                "text": "LOG OUT",
                "height": dp(56),
                "on_release": lambda x="Item 2": self.menu_callback(x),
            }
        ]
        self.menu = MDDropdownMenu(
            items=self.menu_items,
            width_mult=4,
        )

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(GasMenu(name="gas"))
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(GasMenuH2Gas(name="h2gas"))

        return sm

    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Orange" if self.theme_cls.primary_palette == "Orange" else "Orange"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def change_screen(self, screen_name):
        self.root.current = screen_name

    def callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item):
        self.menu.dismiss()
        print('test')

    def change_screen_h2_gas(self, screen_name):
        self.menu.dismiss()
        self.root.current = screen_name

    def insert_to_database(self):
        self.create_database()

        conn = sqlite3.connect('gas_data.db')
        cursor = conn.cursor()

        date = self.root.get_screen('gas').ids.date.text
        shift = self.root.get_screen('gas').ids.shift.text
        temp = self.root.get_screen('gas').ids.temp.text
        n_pressure = self.root.get_screen('gas').ids.n_pressure.text
        p_pressure = self.root.get_screen('gas').ids.p_pressure.text
        n_cylinder_pressure = self.root.get_screen(
            'gas').ids.n_cylinder_pressure.text
        p_pressure_gauge_bhs2 = self.root.get_screen(
            'gas').ids.p_pressure_gauge_bhs2.text
        time = self.root.get_screen('gas').ids.time.text
        p_pressure_gauge_pallet = self.root.get_screen(
            'gas').ids.p_pressure_gauge_pallet.text
        remarks = self.root.get_screen('gas').ids.remarks.text
        s_pressure_gauge = self.root.get_screen(
            'gas').ids.s_pressure_gauge.text

        query = """
            INSERT INTO ShiftData
            (Date, Shift, Temperature, Nitrogen, Pressure, NitrogenCylinderPressure,
            PrimaryPressureGaugeBH2, Time, PrimaryPressureGaugePallet,
            Remarks, SecondaryPressureGaugeBH2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        data = (date, shift, temp, n_pressure, p_pressure, n_cylinder_pressure,
                p_pressure_gauge_bhs2, time, p_pressure_gauge_pallet,
                remarks, s_pressure_gauge)

        if date == '' or shift == '' or temp == '' or n_pressure == '' or p_pressure == '' or n_cylinder_pressure == '' or p_pressure_gauge_bhs2 == '' or time == '' or p_pressure_gauge_pallet == '' or remarks == '' or s_pressure_gauge == '':
            dialog = MDDialog(
                title="Error Something went Wrong",
                radius=[20, 7, 20, 7],
                text="Error: Data fields cannot be empty.",
                buttons=[MDRaisedButton(
                    text="OK", on_release=lambda _: dialog.dismiss())]
            )
            dialog.open()
        else:
            try:
                cursor.execute(query, data)
                conn.commit()
                dialog = MDDialog(
                    title="Successfully Inserted!",
                    text="Data inserted into the database.",
                    radius=[20, 7, 20, 7],
                    buttons=[MDRaisedButton(
                        text="OK", on_release=lambda _: dialog.dismiss())]
                )

                dialog.open()

                print('Success')
            except Exception as e:
                dialog = MDDialog(
                    title="Error Something went Wrong",
                    radius=[20, 7, 20, 7],
                    text=f"Error: {str(e)}.",
                    buttons=[MDRaisedButton(
                        text="OK", on_release=lambda _: dialog.dismiss())]
                )
                dialog.open()

            finally:

                conn.close()


Example().run()
