# main.py
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.utils import platform
from kivy.clock import Clock

import core_lavoro as core

class RassegnaApp(App):
    def build(self):
        self.title = "Rassegna Normativa Lavoro"
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        btn_service = Button(text="Attiva Monitoraggio Background", size_hint_y=None, height=50)
        btn_service.bind(on_press=self.start_background_service)
        root.add(btn_service)
        
        self.status_label = Label(text="Caricamento atti in corso...", size_hint_y=None, height=30)
        root.add(self.status_label)
        
        self.rv = RecycleView()
        root.add(self.rv)
        
        # Avvia il servizio in background e carica i dati
        self.start_background_service()
        Clock.schedule_once(lambda dt: self.carica_dati_nella_gui(), 1)
        
        return root

    def start_background_service(self, *args):
        if platform == 'android':
            from android import AndroidService
            service = AndroidService('Rassegna Monitor', 'running')
            service.start('Inizio servizio background')
            self.status_label.text = "Servizio attivato in background."

    def carica_dati_nella_gui(self):
        try:
            atti = core.raccogli()
            self.rv.data = [{'text': f"[{it['code']}] {it['data_label']}\n{it['titolo'][:80]}..."} for it in atti[:50]]
            self.status_label.text = f"Trovati {len(atti)} atti totali."
        except Exception as e:
            self.status_label.text = f"Errore caricamento GUI: {e}"

if __name__ == '__main__':
    RassegnaApp().run()
