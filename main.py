import tkinter as tk
from tkinter import ttk
import datetime
import requests
from bs4 import BeautifulSoup
import pytz

class PrayerTimesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Namaz Vakitleri ve Günlük Program")
        self.root.geometry("800x600") 
        
        # Namaz vakitleri
        self.prayer_times = {
            "Sabah": "6:29",
            "Öğle": "13:03",
            "İkindi": "15:30",
            "Akşam": "17:46",
            "Yatsı": "19:21"
        }
        
        # Günlük planlar
        self.schedule = [
            ("05:00 - 6:29", "Kuran okuma veya zikir"),
            ("6:29 - 06:52", "Sabah namazı"),
            ("06:52 - 07:52", "İngilizce çalışma (1 saat)"),
            ("07:52 - 08:52", "Kahvaltı ve hazırlık"),
            ("08:52 - 10:30", "1. Yazılım projesi çalışması"),
            ("10:30 - 11:00", "Kısa mola ve hafif atıştırmalık"),
            ("11:00 - 13:03", "2. Yazılım projesi çalışması"),
            ("13:03 - 13:22", "Öğle namazı"),
            ("13:22 - 13:52", "Öğle yemeği"),
            ("13:52 - 14:52", "Dinlenme (1 saat uyku)"),
            ("14:52 - 15:30", "3. Yazılım projesi çalışması"),
            ("15:30 - 15:56", "İkindi namazı ve kısa mola"),
            ("15:56 - 18:20", "Yeni yazılım dilleri ve teknolojiler üzerine çalışma"),
            ("18:20 - 18:43", "Aile ile kısa vakit geçirme"),
            ("17:46 - 18:18", "Akşam namazı"),
            ("18:18 - 19:21", "Akşam yemeği ve aile ile sohbet"),
            ("19:21 - 19:43", "Yatsı namazı"),
            ("19:43 - 22:00", "Aile ile kaliteli zaman veya kişisel aktiviteler"),
            ("22:00 - 22:30", "Kitap okuma (30 dakika)"),
            ("22:30 - 23:00", "Ertesi gün için hazırlık"),
            ("23:00", "Yatış")
        ]
        
        self.setup_ui()
        self.update_current_time()
        self.fetch_prayer_times()
        
    def setup_ui(self):
        # Namaz vakitleri frame
        prayer_frame = ttk.LabelFrame(self.root, text="Namaz Vakitleri")
        prayer_frame.pack(fill="x", padx=5, pady=5)
        
        # Namaz vakitleri display
        prayer_text = " ".join([f"{name}: {time}" for name, time in self.prayer_times.items()])
        self.prayer_label = ttk.Label(prayer_frame, text=prayer_text)
        self.prayer_label.pack(pady=5)
        
        # program frame
        schedule_frame = ttk.LabelFrame(self.root, text="Günlük Program")
        schedule_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # program table oluştur
        self.tree = ttk.Treeview(schedule_frame, columns=("Time", "Activity"), show="headings")
        self.tree.heading("Time", text="Saat")
        self.tree.heading("Activity", text="Aktivite")
        
        # Configure column
        self.tree.column("Time", width=150)
        self.tree.column("Activity", width=600)
        
        # ekle program items
        for time, activity in self.schedule:
            self.tree.insert("", "end", values=(time, activity))
        
        # scrollbar ekle
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # arayüz düzen
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # güncelleme button
        update_button = ttk.Button(self.root, text="Programı Güncelle", command=self.update_schedule)
        update_button.pack(pady=5)
        
    def update_current_time(self):
        # anlık görev
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Önceki vurgulamayı temizle
        for item in self.tree.get_children():
            self.tree.item(item, tags=())
        
        # geçerli zamanı vurgula
        for item in self.tree.get_children():
            time_slot = self.tree.item(item)["values"][0]
            if self.is_current_time_slot(time_slot, current_time):
                self.tree.item(item, tags=("current",))
        
        # vurgulama rengi
        self.tree.tag_configure("current", background="red")
        
        
        self.root.after(60000, self.update_current_time)  # dakikalık yenileme
        
    def is_current_time_slot(self, time_slot, current_time):
        if "-" not in time_slot:
            return False
            
        start_time, end_time = time_slot.split(" - ")
        current_minutes = self.time_to_minutes(current_time)
        start_minutes = self.time_to_minutes(start_time)
        end_minutes = self.time_to_minutes(end_time)
        
        return start_minutes <= current_minutes < end_minutes
        
    def time_to_minutes(self, time_str):
        try:
            hours, minutes = map(int, time_str.split(":"))
            return hours * 60 + minutes
        except:
            return 0
            
    def fetch_prayer_times(self):
        try:
            url = "https://m.dinimizislam.com/NamazVakti_HP/namazvakti.asp?ff=Arial&fs=16"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            
        except Exception as e:
            print(f"Error fetching prayer times: {e}")
            
    def update_schedule(self):
        # Refresh 
        self.update_current_time()
        self.fetch_prayer_times()

if __name__ == "__main__":
    root = tk.Tk()
    app = PrayerTimesApp(root)
    root.mainloop()
