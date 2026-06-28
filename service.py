# service.py
import time
import os
import json
import core_lavoro as core

from jnius import autoclass

Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
NotificationCompat = autoclass('androidx.core.app.NotificationCompat$Builder')

PythonService = autoclass('org.kivy.android.PythonService')
current_service = PythonService.mService

STATE_FILE = os.path.join(os.path.dirname(__file__), "service_state.json")
CHANNEL_ID = "rassegna_lavoro_channel"

def setup_notification_channel():
    name = "Notifiche Rassegna"
    description = "Canale per le novità normative"
    importance = NotificationManager.IMPORTANCE_DEFAULT
    channel = NotificationChannel(CHANNEL_ID, name, importance)
    channel.setDescription(description)
    
    notification_manager = current_service.getSystemService(Context.NOTIFICATION_SERVICE)
    notification_manager.createNotificationChannel(channel)

def send_local_notification(id_notifica, titolo, testo):
    package_name = current_service.getPackageName()
    launch_intent = current_service.getPackageManager().getLaunchIntentForPackage(package_name)
    pending_intent = PendingIntent.getActivity(current_service, id_notifica, launch_intent, PendingIntent.FLAG_IMMUTABLE)

    builder = NotificationCompat(current_service, CHANNEL_ID)
    builder.setContentTitle(titolo)
    builder.setContentText(testo)
    builder.setSmallIcon(current_service.getApplicationInfo().icon)
    builder.setContentIntent(pending_intent)
    builder.setAutoCancel(True)

    notification_manager = current_service.getSystemService(Context.NOTIFICATION_SERVICE)
    notification_manager.notify(id_notifica, builder.build())

def carica_visti():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def salva_visti(uids):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(uids), f)
    except Exception:
        pass

def main():
    setup_notification_channel()
    
    builder_fg = NotificationCompat(current_service, CHANNEL_ID)
    builder_fg.setContentTitle("Rassegna Lavoro")
    builder_fg.setContentText("Monitoraggio novità attivo...")
    builder_fg.setSmallIcon(current_service.getApplicationInfo().icon)
    current_service.startForeground(1, builder_fg.build())

    while True:
        try:
            items = core.raccogli()
            visti = carica_visti()
            
            if not visti:
                salva_visti({it["uid"] for it in items})
            else:
                nuovi = [it for it in items if it["uid"] not in visti]
                for i, it in enumerate(nuovi[:5]):
                    send_local_notification(
                        id_notifica=i + 100,
                        titolo=f"Nuovo atto {it['code']}",
                        testo=it["titolo"][:50] + "..."
                    )
                if nuovi:
                    salva_visti({it["uid"] for it in items} | visti)
                    
        except Exception as e:
            print(f"Errore nel servizio: {e}")
            
        time.sleep(1800)

if __name__ == '__main__':
    main()
