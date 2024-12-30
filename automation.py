import pyautogui
import keyboard
import time
import tkinter as tk
from tkinter import ttk, Frame, messagebox, simpledialog, filedialog
import sys
import threading
import json
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Point:
    x: int
    y: int

class AutoClickerApp:
    def __init__(self):
        # Renkler
        self.colors = {
            'bg': '#F5F7FA',  # Açık gri arka plan
            'text': '#2D3748',  # Koyu gri metin
            'primary': '#4299E1',  # Mavi vurgu
            'secondary': '#A0AEC0',  # Orta gri
            'success': '#48BB78',  # Yeşil
            'danger': '#F56565',  # Kırmızı
            'warning': '#ECC94B',  # Sarı
            'hover': '#3182CE',  # Hover durumu için koyu mavi
            'border': '#E2E8F0'  # Kenarlık rengi
        }
        
        # Stil sabitleri
        self.styles = {
            'font_family': 'Segoe UI',
            'button_padding': '8px 16px',
            'border_radius': 4,
            'spacing': 10,
            'header_font_size': 12,
            'text_font_size': 10,
            'button_font_size': 10
        }

        self.root = tk.Tk()
        self.root.title("Otomasyon")
        self.root.resizable(True, True)
        self.root.minsize(900, 700)  # Minimum pencere boyutunu artırdım
        
        # Ana pencere stili
        self.root.configure(bg=self.colors['bg'])
        
        # ttk stilleri
        style = ttk.Style()
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabelframe', background=self.colors['bg'])
        style.configure('TLabelframe.Label', 
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=(self.styles['font_family'], self.styles['header_font_size'], 'bold')
        )
        style.configure('TLabel',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=(self.styles['font_family'], self.styles['text_font_size'])
        )
        style.configure('TEntry',
            fieldbackground='white',
            borderwidth=1,
            relief='solid',
            font=(self.styles['font_family'], self.styles['text_font_size'])
        )
        
        # Grid ağırlıkları
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # Pencere kapatma protokolü
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # P tuşu ile duraklatma/devam etme
        keyboard.on_press_key('p', self.handle_pause_key)
        
        # Set yönetimi için değişkenler
        self.sets = {}
        self.current_set_id = 1
        self.active_set = 1
        
        # UI elemanları için listeler
        self.coordinates_labels = []
        self.left_buttons = []
        self.right_buttons = []
        self.delay_entries = []
        self.order_entries = []
        self.goto_buttons = []
        self.update_buttons = []
        self.double_buttons = []
        self.set_buttons = []
        self.text_entries = []  # Metin girişi için yeni liste
        
        # Varsayılan değerler
        self.delay_times = ['0.5'] * 20
        
        # Çalışma durumu için değişkenler
        self.running = False
        self.paused = False
        self.recording_mode = False
        self.current_queue_index = 0
        self.execution_queue = []
        self.update_mode = None  # Güncelleme modu için değişken eklendi
        
        # İlk seti oluştur
        self.sets[1] = {
            'name': "Set 1",
            'coordinates': [None] * 20,
            'names': [f"K {i+1}" for i in range(20)],
            'clicks': ['left'] * 20,
            'delays': ['0.5'] * 20,
            'order': list(range(20)),
            'loop_count': 1,
            'texts': [''] * 20  # Her koordinat için metin alanı
        }
        
        # UI kurulumu
        self.setup_ui()

    def setup_ui(self):
        # Menü çubuğu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Yeni", command=self.new_file)
        file_menu.add_command(label="Aç...", command=self.open_file)
        file_menu.add_command(label="Kaydet", command=self.save_file)
        file_menu.add_command(label="Farklı Kaydet...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        
        # Ana container - weight'leri ekledik
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)  # Koordinatlar frame'i için
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Set yönetimi için frame
        set_management_frame = ttk.LabelFrame(main_frame, text="Set Yönetimi", padding="15")
        set_management_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        set_management_frame.grid_columnconfigure(0, weight=1)
        
        # Set butonları için frame
        self.set_buttons_frame = ttk.Frame(set_management_frame)
        self.set_buttons_frame.grid(row=0, column=0, sticky="ew", padx=5)
        
        # Yeni Set Ekle butonu - boyut artırıldı
        add_set_btn = tk.Button(
            self.set_buttons_frame,
            text="+ Yeni Set",
            command=self.add_new_set,
            bg=self.colors['success'],
            fg='white',
            font=('Segoe UI', 10),
            relief=tk.RAISED,
            bd=1,
            width=12
        )
        add_set_btn.grid(row=0, column=0, padx=(0, 15))
        
        # Koordinatlar Frame'i - weight'leri ekledik
        coordinates_frame = ttk.LabelFrame(main_frame, text="Koordinatlar", padding="20")
        coordinates_frame.grid(row=1, column=0, sticky="nsew", padx=self.styles['spacing'], pady=self.styles['spacing'])
        coordinates_frame.grid_rowconfigure(1, weight=1)
        coordinates_frame.grid_columnconfigure(0, weight=1)
        
        # Üst kısım için frame
        top_frame = ttk.Frame(coordinates_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        # Koordinat Kaydetme Modu butonu - boyut artırıldı
        self.coordinate_mode_button = tk.Button(
            top_frame,
            text="📍 Koordinat Kaydetme Modu: Kapalı",
            command=self.toggle_coordinate_mode,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=(self.styles['font_family'], self.styles['button_font_size'], 'bold'),
            width=35,
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        self.coordinate_mode_button.pack(side=tk.LEFT, padx=self.styles['spacing'])
        
        # Döngü sayısı için frame
        loop_frame = ttk.Frame(top_frame)
        loop_frame.pack(side=tk.LEFT, padx=30)
        
        # Döngü sayısı etiketi - font büyütüldü
        loop_label = ttk.Label(loop_frame, text="Döngü Sayısı:", font=('Segoe UI', 10))
        loop_label.pack(side=tk.LEFT, padx=5)
        
        # Döngü sayısı girişi - genişlik artırıldı
        self.loop_count_entry = ttk.Entry(loop_frame, width=7)
        self.loop_count_entry.pack(side=tk.LEFT)
        self.loop_count_entry.insert(0, "1")
        self.loop_count_entry.bind('<FocusOut>', lambda e: (self.save_loop_count(), self.root.focus()))
        self.loop_count_entry.bind('<Return>', lambda e: (self.save_loop_count(), self.root.focus()))
        
        # Koordinat listesi için frame
        coordinates_list_frame = ttk.Frame(coordinates_frame)
        coordinates_list_frame.grid(row=1, column=0, sticky="nsew")
        
        # Sol ve sağ sütunlar için ayrı frame'ler oluştur
        left_column = ttk.Frame(coordinates_list_frame)
        right_column = ttk.Frame(coordinates_list_frame)
        left_column.grid(row=0, column=0, sticky="nsew", padx=5)
        right_column.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Grid ağırlıklarını ayarla
        coordinates_list_frame.grid_columnconfigure(0, weight=1)
        coordinates_list_frame.grid_columnconfigure(1, weight=1)
        
        # Başlık satırı
        headers = ["Koordinat", "Tıklama", "Metin", "Gecikme", "Sıra", "Git", "Güncelle"]
        header_widths = [20, 8, 15, 8, 5, 5, 8]  # Tıklama sütunu için genişliği azalttık
        
        # Her sütun için başlıkları ekle
        for col in [left_column, right_column]:
            for i, (header, width) in enumerate(zip(headers, header_widths)):
                header_label = ttk.Label(
                    col, 
                    text=header, 
                    width=width,
                    font=(self.styles['font_family'], self.styles['header_font_size'], 'bold')
                )
                header_label.grid(row=0, column=i, padx=2, pady=(0, 10))
        
        # Koordinat listesi
        for i in range(20):
            # Hangi sütunda olacağını belirle
            current_frame = left_column if i < 10 else right_column
            row = (i % 10) + 1
            
            # Koordinat etiketi
            coord_label = ttk.Label(current_frame, text=f"K {i+1}: ", width=15)
            coord_label.grid(row=row, column=0, padx=2, pady=2, sticky="w")
            coord_label.bind('<Double-Button-1>', lambda e, idx=i: self.start_edit_label(e, idx))
            self.coordinates_labels.append(coord_label)
            
            # Tıklama butonları için frame
            click_frame = ttk.Frame(current_frame)
            click_frame.grid(row=row, column=1, padx=2, pady=2)
            
            # Sol tık butonu
            left_btn = tk.Button(
                click_frame,
                text="◀",  # Sol ok işareti
                command=lambda x=i: self.toggle_click_type(x, 'left'),
                width=2,
                bg=self.colors['primary'],
                fg='white',
                font=(self.styles['font_family'], 8),
                relief=tk.FLAT,
                cursor='hand2'
            )
            left_btn.pack(side=tk.LEFT, padx=1)
            self.left_buttons.append(left_btn)
            
            # Sağ tık butonu
            right_btn = tk.Button(
                click_frame,
                text="▶",  # Sağ ok işareti
                command=lambda x=i: self.toggle_click_type(x, 'right'),
                width=2,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=(self.styles['font_family'], 8),
                relief=tk.FLAT,
                cursor='hand2'
            )
            right_btn.pack(side=tk.LEFT, padx=1)
            self.right_buttons.append(right_btn)
            
            # Double click butonu
            double_btn = tk.Button(
                click_frame,
                text="⚡",  # Yıldırım işareti
                command=lambda x=i: self.toggle_click_type(x, 'double'),
                width=2,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=(self.styles['font_family'], 8),
                relief=tk.FLAT,
                cursor='hand2'
            )
            double_btn.pack(side=tk.LEFT, padx=1)
            self.double_buttons.append(double_btn)
            
            # Metin girişi alanı
            text_entry = ttk.Entry(current_frame, width=15)
            text_entry.grid(row=row, column=2, padx=2, pady=2)
            text_entry.bind('<Return>', self.clear_focus)
            self.text_entries.append(text_entry)
            
            # Gecikme süresi girişi
            delay_entry = ttk.Entry(current_frame, width=8)
            delay_entry.insert(0, "0.5")
            delay_entry.grid(row=row, column=3, padx=2, pady=2)
            delay_entry.bind('<Return>', self.clear_focus)
            self.delay_entries.append(delay_entry)
            
            # Sıra numarası girişi
            order_entry = ttk.Entry(current_frame, width=5)
            order_entry.insert(0, str(i))
            order_entry.grid(row=row, column=4, padx=2, pady=2)
            order_entry.bind('<Return>', self.clear_focus)
            self.order_entries.append(order_entry)
            
            # Git butonu
            goto_btn = tk.Button(
                current_frame,
                text="Git",
                command=lambda x=i: self.goto_coordinate(x),
                width=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            goto_btn.grid(row=row, column=5, padx=2, pady=2)
            self.goto_buttons.append(goto_btn)
            
            # Güncelle butonu
            update_btn = tk.Button(
                current_frame,
                text="Güncelle",
                command=lambda x=i: self.update_coordinate(x),
                width=8,
                relief=tk.FLAT,
                cursor='hand2'
            )
            update_btn.grid(row=row, column=6, padx=2, pady=2)
            self.update_buttons.append(update_btn)
        
        # Kontrol paneli
        control_panel = ttk.LabelFrame(main_frame, text="Kontrol Paneli", padding="15")
        control_panel.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        control_panel.grid_columnconfigure(0, weight=1)
        
        # Otomasyon Başlat butonu
        self.automation_button = tk.Button(
            control_panel,
            text="▶️ Otomasyonu Başlat",
            command=self.toggle_automation,
            bg=self.colors['success'],
            fg='white',
            font=(self.styles['font_family'], self.styles['button_font_size'], 'bold'),
            width=25,
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        self.automation_button.grid(row=0, column=3, padx=self.styles['spacing'])
        
        # Duraklat butonu
        self.pause_button = tk.Button(
            control_panel,
            text="⏸️ Duraklat",
            command=self.toggle_pause,
            state=tk.DISABLED,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=(self.styles['font_family'], self.styles['button_font_size']),
            width=20,
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        self.pause_button.grid(row=0, column=4, padx=self.styles['spacing'])

        # İşlem Kuyruğu Frame'i
        queue_frame = ttk.LabelFrame(main_frame, text="İşlem Kuyruğu", padding="20")
        queue_frame.grid(row=3, column=0, sticky="ew", padx=self.styles['spacing'], pady=self.styles['spacing'])
        queue_frame.grid_columnconfigure(0, weight=1)
        
        # İşlem kuyruğu için frame
        self.queue_buttons_frame = ttk.Frame(queue_frame)
        self.queue_buttons_frame.grid(row=0, column=0, sticky="ew")
        
        # Kuyruk Temizle butonu
        clear_queue_btn = tk.Button(
            self.queue_buttons_frame,
            text="🗑️ Kuyruğu Temizle",
            command=self.clear_queue,
            bg=self.colors['danger'],
            fg='white',
            font=(self.styles['font_family'], self.styles['button_font_size']),
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        clear_queue_btn.grid(row=0, column=0, padx=self.styles['spacing'])
        
        # Kuyruk listesi için frame
        self.queue_list_frame = ttk.Frame(queue_frame)
        self.queue_list_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        # En son: İlk seti oluştur ve aktif hale getir
        self.create_set_button(1)  # Önce Set 1'i oluştur
        self.root.after(100, lambda: self.switch_set(1))  # Tüm UI elemanları oluştuktan sonra Set 1'i aktif et

        # Root frame'e click event ekle
        self.root.bind('<Button-1>', self.clear_focus)

    def create_set_button(self, set_id):
        """Set butonu oluşturur"""
        # Her set için bir frame oluştur
        set_frame = ttk.Frame(self.set_buttons_frame)
        set_frame.grid(row=0, column=len(self.set_buttons)+1, padx=self.styles['spacing'], sticky="w")
        
        # Set butonu
        set_btn = tk.Button(
            set_frame,
            text=f"Set {set_id}",
            command=lambda: self.switch_set(set_id),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=(self.styles['font_family'], self.styles['button_font_size']),
            relief=tk.RAISED,
            bd=1,
            width=12,
            cursor='hand2'
        )
        set_btn.pack(side=tk.LEFT, padx=2)
        
        # İsim Değiştir butonu
        rename_btn = tk.Button(
            set_frame,
            text="✏️",
            command=lambda: self.rename_set(set_id),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=(self.styles['font_family'], self.styles['button_font_size']),
            relief=tk.FLAT,
            bd=0,
            width=3,
            cursor='hand2'
        )
        rename_btn.pack(side=tk.LEFT, padx=2)
        
        # Kuyruğa Ekle butonu
        add_queue_btn = tk.Button(
            set_frame,
            text="➕",
            command=lambda: self.add_to_queue(set_id),
            bg=self.colors['success'],
            fg='white',
            font=(self.styles['font_family'], self.styles['button_font_size']),
            relief=tk.RAISED,
            bd=1,
            width=3,
            cursor='hand2'
        )
        add_queue_btn.pack(side=tk.LEFT, padx=2)
        
        self.set_buttons.append(set_btn)

    def setup_control_panel(self):
        """Kontrol panelini oluşturur"""
        control_panel = ttk.LabelFrame(self.root, text="Kontrol Paneli", padding="10")
        control_panel.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Otomasyon Başlat butonu
        self.automation_button = tk.Button(
            control_panel,
            text="▶️ Otomasyonu Başlat",
            command=self.toggle_automation,
            bg=self.colors['success'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            width=20
        )
        self.automation_button.grid(row=0, column=2, padx=5)
        
        # Duraklat butonu
        self.pause_button = tk.Button(
            control_panel,
            text="⏸️ Duraklat",
            command=self.toggle_pause,
            state=tk.DISABLED,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Segoe UI', 9),
            width=15
        )
        self.pause_button.grid(row=0, column=3, padx=5)

    def toggle_start_stop(self):
        """Başlat/Durdur butonuna tıklandığında"""
        if not self.running:
            # Başlatma işlemi
            if not self.execution_queue:
                messagebox.showwarning("Uyarı", "İşlem kuyruğu boş!")
                return
            
            try:
                self.loop_count = int(self.loop_entry.get())
                if self.loop_count < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir döngü sayısı girin!")
                return
            
            self.running = True
            self.paused = False
            self.start_stop_button.config(text="Durdur", bg=self.colors['danger'])
            self.pause_button.config(state=tk.NORMAL)
            
            # Kuyruğu işlemeye başla
            self.current_queue_index = 0
            self.process_queue()
            
        else:
            # Durdurma işlemi
            self.running = False
            self.paused = False
            self.start_stop_button.config(text="Başlat", bg=self.colors['success'])
            self.pause_button.config(text="Duraklat", state=tk.DISABLED)

    def process_queue(self):
        """İşlem kuyruğunu işler"""
        if not self.running or self.paused:
            return
        
        try:
            # Kuyrukta set var mı kontrol et
            if not self.execution_queue:
                self.toggle_automation()
                return
            
            # Aktif seti al
            current_set_id = self.execution_queue[self.current_queue_index]
            current_set = self.sets[current_set_id]
            
            # Setin döngü sayısını al
            loop_count = current_set['loop_count']
            
            # Koordinatları işle
            coordinates = current_set['coordinates']
            clicks = current_set['clicks']
            
            # Tüm döngüler tamamlandı mı kontrol et
            if self.current_loop >= loop_count:
                self.current_queue_index += 1
                self.current_loop = 0
                self.current_coord = 0
                
                if self.current_queue_index >= len(self.execution_queue):
                    self.current_queue_index = 0
                    self.running = False
                    self.automation_button.config(
                        text="▶️ Otomasyonu Başlat",
                        bg=self.colors['success']
                    )
                    self.pause_button.config(
                        text="⏸️ Duraklat",
                        bg=self.colors['bg'],
                        state=tk.DISABLED
                    )
                    return
                else:
                    self.root.after(100, self.process_queue)
                return
            
            # Tüm koordinatlar tamamlandı mı kontrol et
            if self.current_coord >= len(coordinates):
                self.current_loop += 1
                self.current_coord = 0
                self.root.after(100, self.process_queue)
                return
            
            # Mevcut koordinatı işle
            coord = coordinates[self.current_coord]
            if coord:
                # Tıklama tipine göre işlem yap
                if clicks[self.current_coord] == 'left':
                    pyautogui.click(coord.x, coord.y, button='left')
                elif clicks[self.current_coord] == 'right':
                    pyautogui.click(coord.x, coord.y, button='right')
                elif clicks[self.current_coord] == 'double':
                    pyautogui.doubleClick(coord.x, coord.y)
                
                # Metin varsa yaz - Setin kendi verisini kullan
                text = current_set['texts'][self.current_coord]
                if text and text.strip():
                    time.sleep(0.1)
                    pyautogui.write(text)
                
                # Gecikme süresini uygula
                try:
                    delay = float(current_set['delays'][self.current_coord])
                except ValueError:
                    delay = 0.5
                
                # Sonraki koordinata geç
                self.current_coord += 1
                
                # Bir sonraki işlemi planla
                self.root.after(int(delay * 1000), self.process_queue)
            else:
                # Boş koordinatı atla
                self.current_coord += 1
                self.root.after(100, self.process_queue)
                
        except Exception as e:
            print(f"İşlem hatası: {e}")
            self.toggle_automation()

    def process_set(self, set_data):
        """Bir seti işler"""
        try:
            # Koordinatları sırayla işle
            for order_idx in range(len(set_data['order'])):
                if not self.running or self.paused:
                    return
                
                # Sıradaki koordinatı bul
                coord_idx = set_data['order'].index(order_idx)
                coord = set_data['coordinates'][coord_idx]
                click_type = set_data['clicks'][coord_idx]
                delay = float(set_data['delays'][coord_idx])
                
                if coord:  # Koordinat kayıtlıysa
                    # Fareyi konumlandır
                    pyautogui.moveTo(coord.x, coord.y)
                    
                    # Tıklama tipine göre işlem yap
                    if click_type == 'left':
                        pyautogui.click()
                    else:
                        pyautogui.rightClick()
                    
                    # Bekleme süresi
                    time.sleep(delay)
                    
        except Exception as e:
            print(f"Set işleme hatası: {str(e)}")

    def loop_coordinates(self):
        """Koordinatları sıraya göre işler"""
        try:
            while self.is_started:
                self.current_loop += 1
                print(f"\nDöngü {self.current_loop} başladı")
                
                # Sıralanmış koordinat indekslerini kullan
                for order_index in self.coordinate_order:
                    if not self.is_started:
                        return
                    
                    if self.is_paused:
                        self.pause_event.wait()
                    
                    coord = self.saved_coordinates[order_index]
                    if coord is not None:
                        self.current_coord = order_index
                        print(f"K {order_index + 1} çalıştırılıyor")
                        
                        # Koordinata git ve tıkla
                        pyautogui.moveTo(coord.x, coord.y)
                        
                        # Tıklama tipini uygula
                        if self.selected_click[order_index] == 'left':
                            pyautogui.click()
                        elif self.selected_click[order_index] == 'right':
                            pyautogui.rightClick()
                        elif self.selected_click[order_index] == 'double':
                            pyautogui.doubleClick()
                        
                        # Bekleme süresini uygula
                        delay = float(self.delay_entries[order_index].get())
                        time.sleep(delay)
                
                print(f"Döngü {self.current_loop} tamamlandı")
                
                # Döngü sayısı kontrolü
                if self.loop_count and self.current_loop >= self.loop_count:
                    self.is_started = False
                    self.start_stop_button.config(text="Başlat", bg=self.colors['success'])
                    break
                
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            self.is_started = False
            self.start_stop_button.config(text="Başlat", bg=self.colors['success'])

    def increase_loop(self):
        try:
            current = int(self.loop_input.get())
            self.loop_input.delete(0, tk.END)
            self.loop_input.insert(0, str(current + 1))
        except ValueError:
            self.loop_input.delete(0, tk.END)
            self.loop_input.insert(0, "0")

    def decrease_loop(self):
        try:
            current = int(self.loop_input.get())
            if current > 0:
                self.loop_input.delete(0, tk.END)
                self.loop_input.insert(0, str(current - 1))
        except ValueError:
            self.loop_input.delete(0, tk.END)
            self.loop_input.insert(0, "0")

    def update_coordinate(self, index):
        """Koordinat güncelleme modunu açar/kapatır"""
        if self.update_mode == index:  # Zaten bu koordinat için güncelleme modundaysa
            # Güncelleme modunu kapat
            self.update_mode = None
            self.update_buttons[index].configure(
                bg=self.colors['bg'],
                fg=self.colors['text']
            )
            self.root.unbind('c')
        else:
            # Varsa önceki güncelleme modunu kapat
            if self.update_mode is not None:
                self.update_buttons[self.update_mode].configure(
                    bg=self.colors['bg'],
                    fg=self.colors['text']
                )
            
            # Yeni güncelleme modunu aç
            self.update_mode = index
            self.update_buttons[index].configure(
                bg=self.colors['primary'],
                fg='white'
            )
            self.root.bind('c', lambda e: self.save_updated_coordinate(index))

    def save_updated_coordinate(self, index, event=None):
        """Güncelleme modunda C tuşuna basıldığında koordinatı kaydeder"""
        if self.update_mode is not None:
            # Mouse pozisyonunu al
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            
            # Koordinatı güncelle
            self.sets[self.active_set]['coordinates'][index] = Point(x, y)
            
            # UI'ı güncelle
            self.coordinates_labels[index].config(
                text=f"K {index+1}: ({x}, {y})"
            )
            
            # Güncelleme modunu kapat
            self.update_mode = None
            self.update_buttons[index].configure(
                bg=self.colors['bg'],
                fg=self.colors['text']
            )
            self.root.unbind('c')

    def save_specific_coordinate(self):
        """Koordinatı kaydet"""
        if not self.is_started:
            print("İşlem başlamadı. Lütfen Başlat butonuna basın.")
            return
        
        current_pos = pyautogui.position()
        
        # Seçili koordinat varsa onu güncelle
        if self.selected_for_update is not None:
            index = self.selected_for_update
            self.saved_coordinates[index] = current_pos
            current_name = self.coordinates_labels[index].cget("text").split(": ")[0]
            self.coordinates_labels[index].config(
                text=f"{current_name}: ({current_pos.x}, {current_pos.y})"
            )
            # Butonu normal haline döndür
            self.update_buttons[index].configure(
                bg=self.colors['bg'],
                fg=self.colors['text']
            )
            self.selected_for_update = None
            print(f"{current_name} güncellendi: {current_pos}")
        else:
            # Normal kayıt işlemi (ilk boş koordinata)
            for i, coord in enumerate(self.saved_coordinates):
                if coord is None:
                    self.saved_coordinates[i] = current_pos
                    current_name = self.coordinates_labels[i].cget("text").split(": ")[0]
                    self.coordinates_labels[i].config(
                        text=f"{current_name}: ({current_pos.x}, {current_pos.y})"
                    )
                    print(f"{current_name} kaydedildi: {current_pos}")
                    break

    def set_left_click(self, index):
        """Sol tıklama modunu aktifleştirir"""
        self.selected_click[index] = 'left'
        self.left_buttons[index].configure(
            bg=self.colors['primary'],
            fg='white',
            relief=tk.RAISED
        )
        self.right_buttons[index].configure(
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED
        )
        self.double_buttons[index].configure(
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED
        )
        print(f"K {index+1} için sol tıklama seçildi")

    def set_right_click(self, index):
        """Sağ tıklama modunu aktifleştirir"""
        self.selected_click[index] = 'right'
        self.right_buttons[index].configure(
            bg=self.colors['primary'],
            fg='white',
            relief=tk.RAISED
        )
        self.left_buttons[index].configure(
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED
        )
        self.double_buttons[index].configure(
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED
        )
        print(f"K {index+1} için sağ tıklama seçildi")

    def set_double_click(self, index):
        """Çift tıklama modunu aktifleştirir"""
        self.selected_click[index] = 'double'
        self.double_buttons[index].configure(
            bg=self.colors['primary'],
            fg='white',
            relief=tk.RAISED
        )
        self.left_buttons[index].configure(
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED
        )
        self.right_buttons[index].configure(
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED
        )
        print(f"K {index+1} için çift tıklama seçildi")

    def setup_keyboard_listener(self):
        """Klavye dinleyicisini ayarla"""
        def on_key_event(e):
            if e.name == 'c':
                self.save_specific_coordinate()
            elif e.name == 'f':
                self.root.quit()
            elif e.name == 'esc':
                self.is_started = False
                self.start_stop_button.config(text="Başlat", bg=self.colors['success'])
                print("İşlem durduruldu.")
            elif e.name == 'p':
                self.toggle_pause()
        
        keyboard.on_press(on_key_event)

    def setup_styles(self):
        style = ttk.Style()
        
        # Normal buton stili
        style.configure('Click.TButton',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            padding=(5, 2),
            font=('Segoe UI', 8)
        )
        
        # Aktif buton stili
        style.configure('Active.TButton',
            background=self.colors['primary'],
            foreground='white',
            padding=(5, 2),
            font=('Segoe UI', 8, 'bold')
        )
        
        # Yeni stil ekledik
        style.configure('Enabled.TEntry',
            fieldbackground='white',
            borderwidth=1,
            relief='solid'
        )

    def start_edit_label(self, event, index):
        """Etiket düzenleme modunu başlatır"""
        label = self.coordinates_labels[index]
        current_name = self.sets[self.active_set]['names'][index]  # Mevcut ismi al
        
        # Düzenleme için Entry widget'ı oluştur
        edit_entry = ttk.Entry(label.master, width=15)
        edit_entry.insert(0, current_name)
        edit_entry.select_range(0, tk.END)  # Metni seç
        
        # Entry'yi yerleştir
        edit_entry.grid(row=(index % 10) + 1, column=0, padx=2, pady=2, sticky="w")
        label.grid_remove()  # Etiketi geçici olarak gizle
        edit_entry.focus()
        
        def save_label(event=None):
            """Yeni etiketi kaydet"""
            new_text = edit_entry.get()
            if not new_text:  # Boş ise varsayılan ismi kullan
                new_text = f"K {index+1}"
            
            # İsmi güncelle
            self.sets[self.active_set]['names'][index] = new_text
            
            # Koordinat değerini al
            coord = self.sets[self.active_set]['coordinates'][index]
            if coord:
                label.configure(text=f"{new_text}: ({coord.x}, {coord.y})")
            else:
                label.configure(text=f"{new_text}: ")
            
            # Düzenleme modundan çık
            edit_entry.destroy()
            label.grid()
        
        def cancel_edit(event=None):
            """Düzenlemeyi iptal et"""
            edit_entry.destroy()
            label.grid()
        
        # Entry olaylarını bağla
        edit_entry.bind('<Return>', save_label)  # Enter tuşu
        edit_entry.bind('<Escape>', cancel_edit)  # ESC tuşu
        edit_entry.bind('<FocusOut>', save_label)  # Fokus kaybı

    def goto_coordinate(self, index):
        """Mouse'u kaydedilen koordinata götürür"""
        coord = self.sets[self.active_set]['coordinates'][index]
        if coord:
            pyautogui.moveTo(coord.x, coord.y)

    def change_set_name(self, set_number):
        """Set ismini değiştir"""
        current_name = self.set_names[set_number]
        new_name = tk.simpledialog.askstring(
            "Set İsmini Değiştir", 
            f"Set {set_number} için yeni isim girin:",
            initialvalue=current_name,
            parent=self.root
        )
        
        if new_name:  # Kullanıcı bir isim girdi ve OK'e bastı
            self.set_names[set_number] = new_name
            self.set_labels[set_number-1].config(text=new_name)

    def switch_set(self, set_id):
        """Seçilen sete geçiş yapar"""
        if set_id not in self.sets:
            return
        
        # Mevcut setin metin verilerini kaydet
        self.sets[self.active_set]['texts'] = [entry.get() for entry in self.text_entries]
        
        # Aktif seti güncelle
        self.active_set = set_id
        
        # Set butonlarının renklerini güncelle
        for i, btn in enumerate(self.set_buttons):
            # Her butonun command'i lambda: self.switch_set(set_id) şeklinde
            # i+1 kullanıyoruz çünkü set_id'ler 1'den başlıyor
            if i+1 == set_id:
                btn.configure(bg=self.colors['primary'], fg='white')
            else:
                btn.configure(bg=self.colors['bg'], fg=self.colors['text'])
        
        # Koordinatları güncelle
        for i, coord in enumerate(self.sets[set_id]['coordinates']):
            coord_name = self.sets[set_id]['names'][i]
            if coord:
                self.coordinates_labels[i].config(
                    text=f"{coord_name}: ({coord.x}, {coord.y})"
                )
            else:
                self.coordinates_labels[i].config(
                    text=f"{coord_name}: "
                )
        
        # Tıklama tiplerini güncelle
        for i, click_type in enumerate(self.sets[set_id]['clicks']):
            # Önce tüm butonları pasif yap
            self.left_buttons[i].configure(bg=self.colors['bg'], fg=self.colors['text'])
            self.right_buttons[i].configure(bg=self.colors['bg'], fg=self.colors['text'])
            self.double_buttons[i].configure(bg=self.colors['bg'], fg=self.colors['text'])
            
            # Aktif olan butonu vurgula
            if click_type == 'left':
                self.left_buttons[i].configure(bg=self.colors['primary'], fg='white')
            elif click_type == 'right':
                self.right_buttons[i].configure(bg=self.colors['primary'], fg='white')
            elif click_type == 'double':
                self.double_buttons[i].configure(bg=self.colors['primary'], fg='white')
        
        # Gecikme sürelerini güncelle
        for i, delay in enumerate(self.sets[set_id]['delays']):
            self.delay_entries[i].delete(0, tk.END)
            self.delay_entries[i].insert(0, delay)
        
        # Sıra numaralarını güncelle
        for i, order in enumerate(self.sets[set_id]['order']):
            self.order_entries[i].delete(0, tk.END)
            self.order_entries[i].insert(0, str(order))
        
        # Döngü sayısını güncelle
        self.loop_count_entry.delete(0, tk.END)
        self.loop_count_entry.insert(0, str(self.sets[set_id]['loop_count']))
        
        # Metin girişlerini güncelle
        for i, text in enumerate(self.sets[set_id]['texts']):
            self.text_entries[i].delete(0, tk.END)
            if text:  # None veya boş string kontrolü
                self.text_entries[i].insert(0, text)

    def update_coordinates_ui(self, set_data):
        """Set verilerine göre UI'ı günceller"""
        # Koordinat etiketlerini güncelle
        for i, (coord, name) in enumerate(zip(set_data['coordinates'], set_data['names'])):
            if coord:
                self.coordinates_labels[i].config(text=f"{name}: ({coord.x}, {coord.y})")
            else:
                self.coordinates_labels[i].config(text=f"{name}: Kayıtsız")
        
        # Tıklama tiplerini güncelle
        for i, click_type in enumerate(set_data['clicks']):
            if click_type == 'left':
                self.left_buttons[i].config(bg=self.colors['primary'], fg='white')
                self.right_buttons[i].config(bg=self.colors['bg'], fg=self.colors['text'])
            else:
                self.left_buttons[i].config(bg=self.colors['bg'], fg=self.colors['text'])
                self.right_buttons[i].config(bg=self.colors['primary'], fg='white')
        
        # Bekleme sürelerini güncelle
        for entry, delay in zip(self.delay_entries, set_data['delays']):
            entry.delete(0, tk.END)
            entry.insert(0, str(delay))
        
        # Sıra numaralarını güncelle
        for i, order_index in enumerate(set_data['order']):
            self.order_entries[order_index].delete(0, tk.END)
            self.order_entries[order_index].insert(0, str(i + 1))

    def toggle_pause(self):
        """Otomasyonu duraklatır/devam ettirir"""
        if not self.running:
            return
        
        self.paused = not self.paused
        
        # UI güncellemesini ana thread'de yap
        self.root.after(0, self._update_pause_button)
        
        if not self.paused:
            # Devam ettirme
            self.root.after(100, self.process_queue)

    def _update_pause_button(self):
        """Duraklat butonunun görünümünü günceller"""
        if self.paused:
            # Duraklatıldı
            self.pause_button.config(
                text="▶️ Devam Et",
                bg=self.colors['success'],
                fg='white'
            )
        else:
            # Devam ediyor
            self.pause_button.config(
                text="⏸️ Duraklat",
                bg=self.colors['bg'],
                fg=self.colors['text']
            )

    def start_loop(self):
        """Loop başlatma işlemi"""
        try:
            # Döngü sayısını al
            loop_count = self.loop_entry.get().strip()
            if loop_count:
                self.loop_count = int(loop_count)
                if self.loop_count <= 0:
                    raise ValueError("Döngü sayısı pozitif olmalıdır")
            else:
                raise ValueError("Döngü sayısı girilmedi")
            
            # Loop'u başlat
            self.is_started = True
            self.start_stop_button.config(text="Durdur", bg=self.colors['danger'])
            print(f"Loop başlatıldı. {self.loop_count} döngü çalışacak.")
            
            # Loop'u ayrı bir thread'de başlat
            threading.Thread(target=self.loop_coordinates, daemon=True).start()
            
        except ValueError as e:
            print(f"Hata: {e}")
            self.is_started = False

    def increase_delay(self, index):
        """Bekleme süresini 0.1 saniye artırır"""
        try:
            current = float(self.delay_entries[index].get())
            new_value = round(current + 0.1, 1)
            self.delay_entries[index].delete(0, tk.END)
            self.delay_entries[index].insert(0, str(new_value))
        except ValueError:
            # Geçersiz değer varsa varsayılan değere dön
            self.delay_entries[index].delete(0, tk.END)
            self.delay_entries[index].insert(0, "0.5")

    def decrease_delay(self, index):
        """Bekleme süresini 0.1 saniye azaltır"""
        try:
            current = float(self.delay_entries[index].get())
            new_value = max(0.1, round(current - 0.1, 1))  # En az 0.1 saniye
            self.delay_entries[index].delete(0, tk.END)
            self.delay_entries[index].insert(0, str(new_value))
        except ValueError:
            # Geçersiz değer varsa varsayılan değere dön
            self.delay_entries[index].delete(0, tk.END)
            self.delay_entries[index].insert(0, "0.5")

    def update_order(self, event, index):
        """Sıra numarası değiştiğinde çalışır"""
        try:
            new_order = int(self.order_entries[index].get()) - 1  # 0-based index
            if 0 <= new_order < 20:
                # Eski ve yeni sırayı al
                old_order = self.coordinate_order.index(index)
                
                # Sıralamayı güncelle
                self.coordinate_order.remove(index)
                self.coordinate_order.insert(new_order, index)
                
                # UI'ı güncelle
                self.update_ui_after_reorder()
            else:
                # Geçersiz sıra - eski değeri geri yükle
                self.order_entries[index].delete(0, tk.END)
                self.order_entries[index].insert(0, str(self.coordinate_order.index(index) + 1))
        except ValueError:
            # Geçersiz girdi - eski değeri geri yükle
            self.order_entries[index].delete(0, tk.END)
            self.order_entries[index].insert(0, str(self.coordinate_order.index(index) + 1))

    def update_ui_after_reorder(self):
        """Sıralama değişince UI'ı günceller"""
        # Tüm sıra numaralarını güncelle
        for i, coord_index in enumerate(self.coordinate_order):
            entry = self.order_entries[coord_index]
            entry.delete(0, tk.END)
            entry.insert(0, str(i + 1))

    def clear_queue(self):
        """İşlem kuyruğunu temizler"""
        # Çalışan otomasyonu durdur
        if self.running:
            self.toggle_automation()
        
        try:
            self.execution_queue = []
            self.current_queue_index = 0
            
            # UI'ı güncelle
            self.update_queue_ui()
                
        except Exception as e:
            print(f"Kuyruk temizleme hatası: {e}")
            messagebox.showerror("Hata", f"Kuyruk temizleme işlemi başarısız: {str(e)}")

    def add_to_queue(self, set_id):
        """Seti kuyruğa ekler"""
        self.execution_queue.append(set_id)
        self.update_queue_ui()

    def update_queue_ui(self):
        """Kuyruk UI'ını günceller"""
        # Kuyruk listesindeki tüm widget'ları temizle
        for widget in self.queue_list_frame.winfo_children():
            widget.destroy()
        
        # Tüm kuyruğu yeniden oluştur
        for i, current_set_id in enumerate(self.execution_queue):
            # Yeni frame oluştur
            queue_item = ttk.Frame(self.queue_list_frame)
            queue_item.grid(row=0, column=i, sticky="ew", padx=2)
            
            # Set ismini al
            set_name = self.sets[current_set_id]['name']
            
            # Set etiketi
            set_label = ttk.Label(queue_item, text=set_name)
            set_label.grid(row=0, column=0, padx=(5, 10))
            
            # Kaldır butonu için özel bir fonksiyon oluştur
            def create_remove_command(sid):
                return lambda: self.remove_from_queue(sid)
            
            # Kaldır butonu
            remove_btn = tk.Button(
                queue_item,
                text="❌",
                command=create_remove_command(current_set_id),
                bg=self.colors['bg'],
                fg=self.colors['danger'],
                font=('Segoe UI', 9),
                relief=tk.FLAT,
                bd=0
            )
            remove_btn.grid(row=0, column=1)

    def remove_from_queue(self, set_id):
        """Seti kuyruktan kaldırır"""
        try:
            if set_id in self.execution_queue:
                # Çalışan otomasyonu durdur
                if self.running and len(self.execution_queue) > 0 and self.execution_queue[0] == set_id:
                    self.toggle_automation()
                
                # Seti kuyruktan kaldır
                self.execution_queue.remove(set_id)
                
                # UI'ı güncelle
                self.update_queue_ui()
                    
        except Exception as e:
            print(f"Kuyruktan set kaldırma hatası: {e}")
            messagebox.showerror("Hata", f"Set kaldırma işlemi başarısız: {str(e)}")

    def toggle_coordinate_mode(self):
        """Koordinat Kaydetme Modunu Açar/Kapatır"""
        if not hasattr(self, 'recording_mode'):
            self.recording_mode = False
        
        if not self.recording_mode:
            # Kaydetme modunu aç
            self.recording_mode = True
            self.coordinate_mode_button.config(
                text="📍 Koordinat Kaydetme Modu: Açık",
                bg=self.colors['danger'],
                fg='white'
            )
            keyboard.on_press_key('c', self.on_coordinate_click)  # Global hotkey olarak C tuşunu ekle
            self.root.attributes('-alpha', 0.95)
            
        else:
            # Kaydetme modunu kapat
            self.recording_mode = False
            self.coordinate_mode_button.config(
                text="📍 Koordinat Kaydetme Modu: Kapalı",
                bg=self.colors['bg'],
                fg=self.colors['text']
            )
            keyboard.unhook_all()  # Tüm global hotkey'leri kaldır
            self.root.attributes('-alpha', 1.0)

    def toggle_automation(self):
        """Otomasyonu başlatır/durdurur"""
        if not self.running:
            # Kuyrukta set var mı kontrol et
            if not self.execution_queue:
                messagebox.showwarning("Uyarı", "İşlem kuyruğu boş!")
                return
                
            # Başlamadan önce mevcut setin metin verilerini kaydet
            self.sets[self.active_set]['texts'] = [entry.get() for entry in self.text_entries]
            
            # Otomasyonu başlat
            self.running = True
            self.paused = False
            
            # Yeni başlatma ise sayaçları sıfırla
            self.current_loop = 0
            self.current_coord = 0
            
            # P tuşunu bağla
            keyboard.on_press_key('p', self.handle_pause_key)
            
            self.automation_button.config(
                text="⏹️ Otomasyonu Durdur",
                bg=self.colors['danger']
            )
            self.pause_button.config(
                text="⏸️ Duraklat",
                bg=self.colors['bg'],
                state=tk.NORMAL
            )
            
            # İşlem kuyruğunu başlat
            self.process_queue()
        else:
            # Otomasyonu durdur
            self.running = False
            self.paused = False
            
            # P tuşu bağlantısını kaldır
            keyboard.unhook_all()
            
            self.automation_button.config(
                text="▶️ Otomasyonu Başlat",
                bg=self.colors['success']
            )
            self.pause_button.config(
                text="⏸️ Duraklat",
                bg=self.colors['bg'],
                state=tk.DISABLED
            )

    def on_coordinate_click(self, event=None):
        """Koordinat kaydetme işlemini yapar"""
        if not self.recording_mode:
            return
        
        # Mouse pozisyonunu al
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        
        # Boş koordinat bul
        for i, coord in enumerate(self.sets[self.active_set]['coordinates']):
            if coord is None:
                # Yeni koordinatı kaydet
                self.sets[self.active_set]['coordinates'][i] = Point(x, y)
                
                # UI'ı güncelle
                self.coordinates_labels[i].config(
                    text=f"K {i+1}: ({x}, {y})"
                )
                
                # İlk boş koordinatı bulduk, döngüden çık
                break

    def add_new_set(self):
        """Yeni set ekler"""
        self.current_set_id += 1
        
        # Yeni set için veri yapısı oluştur
        self.sets[self.current_set_id] = {
            'name': f"Set {self.current_set_id}",
            'coordinates': [None] * 20,
            'names': [f"K {i+1}" for i in range(20)],
            'clicks': ['left'] * 20,
            'delays': ['0.5'] * 20,
            'order': list(range(20)),
            'loop_count': 1,
            'texts': [''] * 20  # Her koordinat için metin alanı
        }
        
        # Set butonunu oluştur
        self.create_set_button(self.current_set_id)

    def rename_set(self, set_id):
        """Set ismini değiştirir"""
        # Yeni isim için input penceresi
        new_name = simpledialog.askstring("Set İsmini Değiştir", 
                                        f"{self.sets[set_id]['name']} için yeni isim girin:",
                                        parent=self.root)
        
        if new_name:
            # Set ismini güncelle
            self.sets[set_id]['name'] = new_name
            
            # Set butonunun textini güncelle
            for i, btn in enumerate(self.set_buttons):
                if i+1 == set_id:  # Buton sırası set_id'yi belirliyor
                    btn.config(text=new_name)
                    break

    def save_loop_count(self, event=None):
        """Döngü sayısını kaydeder"""
        try:
            count = int(self.loop_count_entry.get())
            if count < 1:  # Döngü sayısı en az 1 olmalı
                count = 1
                self.loop_count_entry.delete(0, tk.END)
                self.loop_count_entry.insert(0, "1")
            self.sets[self.active_set]['loop_count'] = count
        except ValueError:
            # Geçersiz değer girilirse varsayılan değere dön
            self.loop_count_entry.delete(0, tk.END)
            self.loop_count_entry.insert(0, str(self.sets[self.active_set]['loop_count']))

    def clear_focus(self, event=None):
        """Tüm input alanlarından focusu kaldırır"""
        # Eğer tıklanan yer bir Entry widget değilse focusu kaldır
        if event and not isinstance(event.widget, ttk.Entry):
            self.root.focus()

    def toggle_click_type(self, index, click_type):
        """Tıklama tipini değiştirir"""
        # Tüm butonları pasif renge çevir
        self.left_buttons[index].configure(bg=self.colors['bg'], fg=self.colors['text'])
        self.right_buttons[index].configure(bg=self.colors['bg'], fg=self.colors['text'])
        self.double_buttons[index].configure(bg=self.colors['bg'], fg=self.colors['text'])
        
        # Seçilen butonu aktif yap
        if click_type == 'left':
            self.left_buttons[index].configure(bg=self.colors['primary'], fg='white')
            self.sets[self.active_set]['clicks'][index] = 'left'
        elif click_type == 'right':
            self.right_buttons[index].configure(bg=self.colors['primary'], fg='white')
            self.sets[self.active_set]['clicks'][index] = 'right'
        elif click_type == 'double':
            self.double_buttons[index].configure(bg=self.colors['primary'], fg='white')
            self.sets[self.active_set]['clicks'][index] = 'double'

    def handle_pause_key(self, event):
        """P tuşuna basıldığında çağrılır"""
        if self.running:
            self.root.after(0, self.toggle_pause)

    def toggle_pause(self):
        """Otomasyonu duraklatır/devam ettirir"""
        if not self.running:
            return
        
        self.paused = not self.paused
        
        if self.paused:
            # Duraklatıldı
            self.pause_button.config(
                text="▶️ Devam Et",
                bg=self.colors['success'],
                fg='white'
            )
        else:
            # Devam ediyor
            self.pause_button.config(
                text="⏸️ Duraklat",
                bg=self.colors['bg'],
                fg=self.colors['text']
            )
            # Devam ettirme
            self.root.after(100, self.process_queue)

    def new_file(self):
        """Yeni dosya oluşturur"""
        if messagebox.askokcancel("Yeni", "Tüm setler silinecek. Emin misiniz?"):
            # Setleri temizle
            self.sets.clear()
            
            # İlk seti oluştur
            self.sets[1] = {
                'name': "Set 1",
                'coordinates': [None] * 20,
                'names': [f"K {i+1}" for i in range(20)],
                'clicks': ['left'] * 20,
                'delays': ['0.5'] * 20,
                'order': list(range(20)),
                'loop_count': 1,
                'texts': [''] * 20  # Her koordinat için metin alanı
            }
            
            # Set butonlarını temizle
            for btn in self.set_buttons:
                btn.destroy()
            self.set_buttons.clear()
            
            # İlk set butonunu oluştur
            self.create_set_button(1)
            
            # Aktif seti ayarla
            self.active_set = 1
            self.current_set_id = 1
            
            # UI'ı güncelle
            self.switch_set(1)

    def save_file(self):
        """Mevcut dosyaya kaydeder"""
        if not hasattr(self, 'current_file'):
            return self.save_as_file()
        
        try:
            # Mevcut setin metin verilerini kaydet
            self.sets[self.active_set]['texts'] = [entry.get() for entry in self.text_entries]
            
            data = {
                'sets': {},
                'active_set': self.active_set,
                'current_set_id': self.current_set_id,
                'execution_queue': self.execution_queue
            }
            
            # Her seti kaydet
            for set_id, set_data in self.sets.items():
                data['sets'][str(set_id)] = {
                    'name': set_data['name'],
                    'coordinates': [(coord.x, coord.y) if coord else None 
                                  for coord in set_data['coordinates']],
                    'names': set_data['names'],
                    'clicks': set_data['clicks'],
                    'delays': set_data['delays'],
                    'order': set_data['order'],
                    'loop_count': set_data['loop_count'],
                    'texts': set_data['texts']  # Metin verilerini kaydet
                }
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Başarılı", "Dosya kaydedildi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası: {str(e)}")

    def save_as_file(self):
        """Farklı dosyaya kaydeder"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON dosyaları", "*.json"), ("Tüm dosyalar", "*.*")],
            title="Farklı Kaydet"
        )
        
        if file_path:
            self.current_file = file_path
            return self.save_file()

    def open_file(self):
        """Dosyadan yükler"""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON dosyaları", "*.json"), ("Tüm dosyalar", "*.*")],
            title="Dosya Aç"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Mevcut setleri temizle
            self.sets.clear()
            for btn in self.set_buttons:
                btn.destroy()
            self.set_buttons.clear()
            
            # Setleri yükle
            for set_id, set_data in data['sets'].items():
                set_id = int(set_id)
                self.sets[set_id] = {
                    'name': set_data['name'],
                    'coordinates': [Point(x, y) if coords else None 
                                  for coords in set_data['coordinates']
                                  for x, y in ([coords] if coords else [(None, None)])],
                    'names': set_data['names'],
                    'clicks': set_data['clicks'],
                    'delays': set_data['delays'],
                    'order': set_data['order'],
                    'loop_count': set_data['loop_count'],
                    'texts': set_data.get('texts', [''] * 20)  # Metin verilerini yükle, yoksa boş liste
                }
                
                # Set butonlarını oluştur
                self.create_set_button(set_id)
            
            # Diğer verileri yükle
            self.active_set = data['active_set']
            self.current_set_id = data['current_set_id']
            self.execution_queue = data.get('execution_queue', [])  # Kuyruğu yükle, yoksa boş liste
            
            # Dosya yolunu kaydet
            self.current_file = file_path
            
            # UI'ı güncelle
            self.switch_set(self.active_set)
            self.update_queue_ui()  # Kuyruk UI'ını güncelle
            
            messagebox.showinfo("Başarılı", "Dosya yüklendi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yükleme hatası: {str(e)}")

    def on_closing(self):
        """Pencere kapatıldığında çağrılır"""
        if messagebox.askokcancel("Çıkış", "Değişiklikleri kaydetmek ister misiniz?"):
            self.save_file()
        
        if messagebox.askokcancel("Çıkış", "Programdan çıkmak istiyor musunuz?"):
            self.root.destroy()

    def rename_coordinate(self, index):
        """Koordinat ismini değiştirir"""
        current_name = self.sets[self.active_set]['names'][index]
        new_name = simpledialog.askstring(
            "Koordinat İsmini Değiştir",
            f"{current_name} için yeni isim girin:",
            parent=self.root,
            initialvalue=current_name
        )
        
        if new_name:
            # İsmi güncelle
            self.sets[self.active_set]['names'][index] = new_name
            
            # Etiketi güncelle
            coord = self.sets[self.active_set]['coordinates'][index]
            if coord:
                self.coordinates_labels[index].config(
                    text=f"{new_name}: ({coord.x}, {coord.y})"
                )
            else:
                self.coordinates_labels[index].config(
                    text=f"{new_name}: "
                )

    # [Diğer metodlar buraya eklenecek]

if __name__ == "__main__":
    app = AutoClickerApp()
    app.root.mainloop()

