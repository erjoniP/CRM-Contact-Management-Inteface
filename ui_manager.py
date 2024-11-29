from datetime import datetime

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from functools import  partial
import csv

from contact_manager import ContactManager

CSV_file = "contacts_info.csv"

class ContactManagementApp(App):

    def build(self):

        self.manager = ContactManager(db_config={'dbname': 'xxxxx',
                                                 'user': 'xxxx',
                                                 'password': 'xxxxx',
                                                 'host': 'localhost',
                                                 'port': 5432})
        self.edit_mode = False
        self.current_edit_id = None

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        header = Label(text="CRM - Contact Management", font_size="22sp")
        layout.add_widget(header)

        full_layout = GridLayout(cols=2)
        full_layout.bind(minimum_height=full_layout.setter("height"))

        self.name_input = TextInput(hint_text="Name", multiline=False)
        self.email_input = TextInput(hint_text="Email", multiline=False)
        self.phone_input = TextInput(hint_text="Phone Number", multiline=False)
        full_layout.add_widget(Label(text="Name:"))
        full_layout.add_widget(self.name_input)
        full_layout.add_widget(Label(text="Email:"))
        full_layout.add_widget(self.email_input)
        full_layout.add_widget(Label(text="Phone:"))
        full_layout.add_widget(self.phone_input)
        layout.add_widget(full_layout)

        submit_button = Button(text="Submit", height=40)
        self.contacts = []

        submit_button.bind(on_press=self.add_edit_contact)
        full_layout.add_widget(submit_button)

        self.contact_list = GridLayout(cols=5, spacing=10, padding=10)
        self.contact_list.bind(minimum_height= self.contact_list.setter("height"))

        scrollview = ScrollView(size_hint=(1, 1))
        scrollview.add_widget(self.contact_list)

        layout.add_widget(scrollview)

        self.update_contact_list()

        return layout

    def add_edit_contact(self, instance):
        name = self.name_input.text.strip()
        email = self.email_input.text.strip()
        phone = self.phone_input.text.strip()

        if not name or not email or not phone:
            self.show_popup("Error", "Please enter data on all fields!")
            return

        try:
            if self.edit_mode:
                self.manager.update_contact(self.current_edit_id, name, email, phone)
            else:
                self.manager.add_contact(name, email, phone)
        except ValueError as e:
            self.show_popup("Error", str(e))

        self.name_input.text = ""
        self.email_input.text = ""
        self.phone_input.text = ""
        self.edit_mode = False
        self.current_edit_id = None

        self.update_contact_list()

    def update_contact_list(self):
        self.contact_list.clear_widgets()

        contacts = self.manager.get_contacts()
        for contact in contacts:
            self.contact_list.add_widget(Label(text=contact['Name'], size_hint_y=None, height=40))
            self.contact_list.add_widget(Label(text=contact['Email'], size_hint_y=None, height=40))
            self.contact_list.add_widget(Label(text=contact['Phone'], size_hint_y=None, height=40))

            edit_button = Button(text="Edit", size_hint_y=None, height=40)
            delete_button = Button(text="Delete", size_hint_y=None, height=40)

            edit_button.bind(on_press=partial(self.update_edit_form, contact['ID']))
            delete_button.bind(on_press=partial(self.delete_contact, contact['ID']))
            self.contact_list.add_widget(edit_button)
            self.contact_list.add_widget(delete_button)

    def update_edit_form(self, contact_id, instance):
        contact = next((c for c in self.manager.get_contacts() if c['ID'] == contact_id), None)
        if contact:
            self.name_input.text = contact['Name']
            self.email_input.text = contact['Email']
            self.phone_input.text = contact['Phone']
            self.edit_mode = True
            self.current_edit_id = contact_id

    def delete_contact(self, contact_id, instance):
        self.manager.delete_contact(contact_id)
        self.update_contact_list()

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10)
        popup_label = Label(text=message)
        close_button = Button(text="Close", size_hint_y=None, height=40)
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.6, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    ContactManagementApp().run()
