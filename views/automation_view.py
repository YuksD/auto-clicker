import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from utils.constants import Constants
from viewmodels.automation_viewmodel import AutomationViewModel

class AutomationView(tk.Tk):
    def __init__(self, viewmodel: AutomationViewModel):
        super().__init__()
        
        self.viewmodel = viewmodel
        self.constants = Constants()
        
        # UI elemanları için listeler
        self.coordinates_labels = []
        self.left_buttons = []
        self.right_buttons = []
        self.double_buttons = []
        self.text_entries = []
        self.delay_entries = []
        self.order_entries = []
        self.goto_buttons = []
        self.update_buttons = []
        self.set_buttons = []
        
        # Aktif koordinat indeksi
        self.active_coordinate_index = 0
        
        # Pencere ayarları
        self.setup_window()
        # UI kurulumu
        self.setup_ui()
        
        # ViewModel callback'lerini ayarla
        self.viewmodel.on_state_changed = self.update_pause_state
        self.viewmodel.on_ui_update = self.update_ui
        self.viewmodel.on_get_coordinate_data = self.get_coordinate_data
        self.viewmodel.on_coordinate_saved = self.handle_coordinate_saved
        
        # Tıklama event'ini bağla
        self.bind('<Button-1>', self.handle_click)
        
        # İlk seti oluştur ve göster
        first_set = self.viewmodel.get_set_names()[0]
        self.add_set_button(first_set)
        self.switch_set(first_set)
    
    def handle_click(self, event):
        """Herhangi bir yere tıklandığında çağrılır"""
        # Eğer tıklanan widget bir Entry değilse odağı temizle
        clicked_widget = event.widget
        if not isinstance(clicked_widget, ttk.Entry) and not isinstance(clicked_widget, tk.Entry):
            self.focus_set()
        
        # Event'in normal işlenmesine devam et
        return "break"
    
    def setup_window(self):
        """Pencere ayarlarını yapar"""
        self.title("Otomasyon")
        self.resizable(True, True)
        self.minsize(900, 700)
        self.configure(bg=self.constants.COLORS['bg'])
        
        # Grid ağırlıkları
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Pencere kapatma protokolü
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # ttk stilleri
        self.setup_styles()
    
    def setup_styles(self):
        """ttk stillerini ayarlar"""
        style = ttk.Style()
        style.configure('TFrame', background=self.constants.COLORS['bg'])
        style.configure('TLabelframe', background=self.constants.COLORS['bg'])
        style.configure('TLabelframe.Label', 
            background=self.constants.COLORS['bg'],
            foreground=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 
                  self.constants.STYLES['header_font_size'], 
                  'bold')
        )
        style.configure('TLabel',
            background=self.constants.COLORS['bg'],
            foreground=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 
                  self.constants.STYLES['text_font_size'])
        )
        style.configure('Header.TLabel',
            background=self.constants.COLORS['bg'],
            foreground=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 
                  self.constants.STYLES['header_font_size'],
                  'bold')
        )
        style.configure('TEntry',
            fieldbackground='white',
            borderwidth=1,
            relief='solid',
            font=(self.constants.STYLES['font_family'], 
                  self.constants.STYLES['text_font_size'])
        )
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        # Ana container
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Menü çubuğu
        self.create_menu()
        
        # Set yönetimi
        self.create_set_management(main_frame)
        
        # Koordinatlar
        self.create_coordinates_frame(main_frame)
        
        # Kontrol paneli
        self.create_control_panel(main_frame)
        
        # İşlem kuyruğu
        self.create_queue_frame(main_frame)
    
    def create_menu(self):
        """Menü çubuğunu oluşturur"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Yeni", command=self.new_file)
        file_menu.add_command(label="Aç...", command=self.open_file)
        file_menu.add_command(label="Kaydet", command=self.save_file)
        file_menu.add_command(label="Farklı Kaydet...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.quit) 
    
    def create_set_management(self, parent):
        """Set yönetimi frame'ini oluşturur"""
        set_management_frame = ttk.LabelFrame(parent, text="Set Yönetimi", padding="15")
        set_management_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        set_management_frame.grid_columnconfigure(1, weight=1)  # Set butonları için
        
        # Sol taraf - Yeni Set Ekle butonu
        left_frame = ttk.Frame(set_management_frame)
        left_frame.grid(row=0, column=0, sticky="w", padx=5)
        
        # Yeni Set Ekle butonu
        add_set_btn = tk.Button(
            left_frame,
            text="+ Yeni Set",
            command=self.add_new_set,
            bg=self.constants.COLORS['success'],
            fg='white',
            font=(self.constants.STYLES['font_family'], 10),
            relief=tk.RAISED,
            bd=1,
            width=12
        )
        add_set_btn.pack(side=tk.LEFT, padx=5)
        
        # Sağ taraf - Set butonları için scrollable frame
        right_frame = ttk.Frame(set_management_frame)
        right_frame.grid(row=0, column=1, sticky="ew", padx=5)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(right_frame, height=40)
        scrollbar = ttk.Scrollbar(right_frame, orient="horizontal", command=canvas.xview)
        self.set_buttons_frame = ttk.Frame(canvas)
        
        # Scrollbar yapılandırması
        canvas.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame'i canvas'a yerleştir
        canvas_frame = canvas.create_window((0, 0), window=self.set_buttons_frame, anchor="nw")
        
        # Canvas yeniden boyutlandırma
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.set_buttons_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
    
    def create_coordinates_frame(self, parent):
        """Koordinatlar frame'ini oluşturur"""
        coordinates_frame = ttk.LabelFrame(parent, text="Koordinatlar", padding="20")
        coordinates_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        coordinates_frame.grid_rowconfigure(1, weight=1)
        coordinates_frame.grid_columnconfigure(0, weight=1)
        
        # Üst kısım için frame
        top_frame = ttk.Frame(coordinates_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        # Koordinat Kaydetme Modu butonu
        self.coordinate_mode_button = tk.Button(
            top_frame,
            text="📍 Koordinat Kaydetme Modu: Kapalı",
            command=self.toggle_coordinate_mode,
            bg=self.constants.COLORS['bg'],
            fg=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 
                  self.constants.STYLES['button_font_size'], 
                  'bold'),
            width=35,
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        self.coordinate_mode_button.pack(side=tk.LEFT, padx=10)
        
        # Döngü sayısı için frame
        loop_frame = ttk.Frame(top_frame)
        loop_frame.pack(side=tk.LEFT, padx=30)
        
        # Döngü sayısı etiketi
        loop_label = ttk.Label(loop_frame, text="Döngü Sayısı:", 
                             font=(self.constants.STYLES['font_family'], 10))
        loop_label.pack(side=tk.LEFT, padx=5)
        
        # Döngü sayısı girişi
        self.loop_count_entry = ttk.Entry(loop_frame, width=7)
        self.loop_count_entry.pack(side=tk.LEFT)
        self.loop_count_entry.insert(0, "1")
        self.loop_count_entry.bind('<FocusOut>', self.save_loop_count)
        self.loop_count_entry.bind('<Return>', self.save_loop_count)
        
        # Koordinat listesi için frame
        self.create_coordinates_list(coordinates_frame)
    
    def create_coordinates_list(self, parent):
        """Koordinat listesini oluşturur"""
        coordinates_list_frame = ttk.Frame(parent)
        coordinates_list_frame.grid(row=1, column=0, sticky="nsew")
        
        # Sol ve sağ sütunlar
        left_column = ttk.Frame(coordinates_list_frame)
        right_column = ttk.Frame(coordinates_list_frame)
        left_column.grid(row=0, column=0, sticky="nsew", padx=5)
        right_column.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Grid ağırlıkları
        coordinates_list_frame.grid_columnconfigure(0, weight=1)
        coordinates_list_frame.grid_columnconfigure(1, weight=1)
        
        # Başlıklar
        headers = ["Koordinat", "Tıklama", "Metin", "Gecikme", "Sıra", "Git", "Güncelle"]
        header_widths = [20, 8, 15, 8, 5, 5, 8]
        
        # Her sütun için başlıkları ekle
        for col in [left_column, right_column]:
            for i, (header, width) in enumerate(zip(headers, header_widths)):
                header_label = ttk.Label(
                    col, 
                    text=header, 
                    width=width,
                    style='Header.TLabel'
                )
                header_label.grid(row=0, column=i, padx=2, pady=(0, 10))
        
        # Koordinat listesi
        self.create_coordinate_rows(left_column, right_column)
    
    def create_coordinate_rows(self, left_column, right_column):
        """Koordinat satırlarını oluşturur"""
        for i in range(20):
            current_frame = left_column if i < 10 else right_column
            row = (i % 10) + 1
            
            # Her satır için UI elemanlarını oluştur
            self.create_coordinate_row(current_frame, row, i)
    
    def create_coordinate_row(self, parent, row, index):
        """Tek bir koordinat satırı oluşturur"""
        # Koordinat etiketi
        coord_label = ttk.Label(parent, text=f"K {index+1}: ", width=15)
        coord_label.grid(row=row, column=0, padx=2, pady=2, sticky="w")
        coord_label.bind('<Double-Button-1>', 
                        lambda e, idx=index: self.start_edit_label(e, idx))
        self.coordinates_labels.append(coord_label)
        
        # Tıklama butonları için frame
        click_frame = ttk.Frame(parent)
        click_frame.grid(row=row, column=1, padx=2, pady=2)
        
        # Tıklama butonlarını oluştur
        self.create_click_buttons(click_frame, index)
        
        # Metin girişi
        text_entry = ttk.Entry(parent, width=15)
        text_entry.grid(row=row, column=2, padx=2, pady=2)
        text_entry.bind('<FocusOut>', self.save_current_set_data)
        self.text_entries.append(text_entry)
        
        # Gecikme süresi girişi
        delay_entry = ttk.Entry(parent, width=8)
        delay_entry.insert(0, "0.5")
        delay_entry.grid(row=row, column=3, padx=2, pady=2)
        delay_entry.bind('<FocusOut>', self.save_current_set_data)
        self.delay_entries.append(delay_entry)
        
        # Sıra numarası girişi
        order_entry = ttk.Entry(parent, width=5)
        order_entry.insert(0, str(index))
        order_entry.grid(row=row, column=4, padx=2, pady=2)
        order_entry.bind('<FocusOut>', self.save_current_set_data)
        self.order_entries.append(order_entry)
        
        # Git butonu
        goto_btn = tk.Button(
            parent,
            text="Git",
            command=lambda: self.goto_coordinate(index),
            width=5,
            relief=tk.FLAT,
            cursor='hand2'
        )
        goto_btn.grid(row=row, column=5, padx=2, pady=2)
        self.goto_buttons.append(goto_btn)
        
        # Güncelle butonu
        update_btn = tk.Button(
            parent,
            text="Güncelle",
            command=lambda: self.update_coordinate(index),
            width=8,
            relief=tk.FLAT,
            cursor='hand2',
            bg=self.constants.COLORS['primary'],
            fg='white'
        )
        update_btn.grid(row=row, column=6, padx=2, pady=2)
        self.update_buttons.append(update_btn)
    
    def create_click_buttons(self, parent, index):
        """Tıklama butonlarını oluşturur"""
        # Sol tık butonu
        left_btn = tk.Button(
            parent,
            text="◀",
            command=lambda: self.toggle_click_type(index, 'left'),
            width=2,
            bg=self.constants.COLORS['primary'],
            fg='white',
            font=(self.constants.STYLES['font_family'], 8),
            relief=tk.FLAT,
            cursor='hand2'
        )
        left_btn.pack(side=tk.LEFT, padx=1)
        self.left_buttons.append(left_btn)
        
        # Sağ tık butonu
        right_btn = tk.Button(
            parent,
            text="▶",
            command=lambda: self.toggle_click_type(index, 'right'),
            width=2,
            bg=self.constants.COLORS['bg'],
            fg=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 8),
            relief=tk.RAISED,
            cursor='hand2'
        )
        right_btn.pack(side=tk.LEFT, padx=1)
        self.right_buttons.append(right_btn)
        
        # Double click butonu
        double_btn = tk.Button(
            parent,
            text="⚡",
            command=lambda: self.toggle_click_type(index, 'double'),
            width=2,
            bg=self.constants.COLORS['bg'],
            fg=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 8),
            relief=tk.RAISED,
            cursor='hand2'
        )
        double_btn.pack(side=tk.LEFT, padx=1)
        self.double_buttons.append(double_btn)
    
    def create_row_elements(self, parent, row, index):
        """Satırdaki diğer UI elemanlarını oluşturur"""
        # Metin girişi
        text_entry = ttk.Entry(parent, width=15)
        text_entry.grid(row=row, column=2, padx=2, pady=2)
        text_entry.bind('<Return>', self.clear_focus)
        self.text_entries.append(text_entry)
        
        # Gecikme süresi girişi
        delay_entry = ttk.Entry(parent, width=8)
        delay_entry.insert(0, "0.5")
        delay_entry.grid(row=row, column=3, padx=2, pady=2)
        delay_entry.bind('<Return>', self.clear_focus)
        self.delay_entries.append(delay_entry)
        
        # Sıra numarası girişi
        order_entry = ttk.Entry(parent, width=5)
        order_entry.insert(0, str(index))
        order_entry.grid(row=row, column=4, padx=2, pady=2)
        order_entry.bind('<Return>', self.clear_focus)
        self.order_entries.append(order_entry)
        
        # Git butonu
        goto_btn = tk.Button(
            parent,
            text="Git",
            command=lambda: self.goto_coordinate(index),
            width=5,
            relief=tk.FLAT,
            cursor='hand2'
        )
        goto_btn.grid(row=row, column=5, padx=2, pady=2)
        self.goto_buttons.append(goto_btn)
        
        # Güncelle butonu
        update_btn = tk.Button(
            parent,
            text="Güncelle",
            command=lambda: self.update_coordinate(index),
            width=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        update_btn.grid(row=row, column=6, padx=2, pady=2)
        self.update_buttons.append(update_btn)
    
    def create_control_panel(self, parent):
        """Kontrol panelini oluşturur"""
        control_panel = ttk.LabelFrame(parent, text="Kontrol Paneli", padding="15")
        control_panel.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        control_panel.grid_columnconfigure(0, weight=1)
        
        # Butonlar için frame
        buttons_frame = ttk.Frame(control_panel)
        buttons_frame.grid(row=0, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure(1, weight=1)  # Ortala
        
        # Otomasyon Başlat butonu
        self.automation_button = tk.Button(
            buttons_frame,
            text="▶️ Otomasyonu Başlat",
            command=self.toggle_automation,
            bg=self.constants.COLORS['success'],
            fg='white',
            font=(self.constants.STYLES['font_family'], 
                  self.constants.STYLES['button_font_size'], 
                  'bold'),
            width=25,
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        self.automation_button.grid(row=0, column=1, padx=10)
        
        # Duraklat butonu
        self.pause_button = tk.Button(
            buttons_frame,
            text="⏸️ Duraklat (P)",
            command=self.toggle_pause,
            state=tk.DISABLED,
            bg=self.constants.COLORS['bg'],
            fg=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 
                  self.constants.STYLES['button_font_size']),
            width=20,
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        self.pause_button.grid(row=0, column=2, padx=10)
    
    def create_queue_frame(self, parent):
        """İşlem kuyruğu frame'ini oluşturur"""
        queue_frame = ttk.LabelFrame(parent, text="İşlem Kuyruğu", padding="15")
        queue_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        queue_frame.grid_columnconfigure(0, weight=1)
        
        # Kuyruk listesi
        self.queue_listbox = tk.Listbox(
            queue_frame,
            height=5,
            selectmode=tk.SINGLE,
            font=(self.constants.STYLES['font_family'], 10),
            bg='white',
            relief=tk.SUNKEN,
            bd=1
        )
        self.queue_listbox.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Kuyruk butonları için frame
        queue_buttons_frame = ttk.Frame(queue_frame)
        queue_buttons_frame.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        
        # Kuyruğa Ekle butonu
        add_to_queue_btn = tk.Button(
            queue_buttons_frame,
            text="➕ Kuyruğa Ekle",
            command=self.add_to_queue,
            bg=self.constants.COLORS['primary'],
            fg='white',
            font=(self.constants.STYLES['font_family'], 10),
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        add_to_queue_btn.pack(side=tk.RIGHT, padx=5)
        
        # Kuyruktan Çıkar butonu
        remove_from_queue_btn = tk.Button(
            queue_buttons_frame,
            text="➖ Kuyruktan Çıkar",
            command=self.remove_from_queue,
            bg=self.constants.COLORS['danger'],
            fg='white',
            font=(self.constants.STYLES['font_family'], 10),
            relief=tk.RAISED,
            bd=1,
            cursor='hand2'
        )
        remove_from_queue_btn.pack(side=tk.RIGHT, padx=5)
    
    # Event Handlers
    def on_closing(self):
        """Uygulama kapatılırken çağrılır"""
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinize emin misiniz?"):
            self.viewmodel.cleanup()
            self.quit()
    
    def clear_focus(self, event=None):
        """Odağı temizler"""
        self.focus_set()
    
    def toggle_coordinate_mode(self):
        """Koordinat kaydetme modunu açıp kapatır"""
        is_active = self.viewmodel.toggle_coordinate_mode()
        
        # Buton rengini ve yazısını güncelle
        if is_active:
            self.coordinate_mode_button.config(
                text="📍 Koordinat Kaydetme Modu: Açık (C ile kaydet)",
                bg=self.constants.COLORS['success']
            )
            # İlk boş koordinatı seç
            self.select_next_empty_coordinate()
        else:
            self.coordinate_mode_button.config(
                text="📍 Koordinat Kaydetme Modu: Kapalı",
                bg=self.constants.COLORS['bg']
            )
            self.active_coordinate_index = 0
    
    def select_next_empty_coordinate(self):
        """Bir sonraki boş koordinatı seçer"""
        set_data = self.viewmodel.get_active_set_data()
        if set_data:
            coordinates = set_data['coordinates']
            for i in range(20):
                if i >= len(coordinates) or not coordinates[i].get('position'):
                    self.active_coordinate_index = i
                    # Seçili koordinatı vurgula
                    self.highlight_active_coordinate()
                    return
    
    def highlight_active_coordinate(self):
        """Aktif koordinatı vurgular"""
        for i, label in enumerate(self.coordinates_labels):
            if i == self.active_coordinate_index:
                label.configure(foreground=self.constants.COLORS['success'])
            else:
                label.configure(foreground=self.constants.COLORS['text'])
    
    def handle_coordinate_saved(self, position):
        """Koordinat kaydedildiğinde çağrılır"""
        if self.active_coordinate_index < 20:
            # Koordinatı kaydet
            self.viewmodel.update_coordinate_position(self.active_coordinate_index, position)
            
            # UI'ı güncelle
            self.update_ui()
            
            # Bir sonraki boş koordinata geç
            self.active_coordinate_index += 1
            self.select_next_empty_coordinate()
            
            # Sesli bildirim
            self.bell()
    
    def toggle_click_type(self, index, click_type):
        """Tıklama tipini değiştirir"""
        active_type = self.viewmodel.toggle_click_type(index, click_type)
        
        # Butonların görünümünü güncelle
        buttons = {
            'left': self.left_buttons[index],
            'right': self.right_buttons[index],
            'double': self.double_buttons[index]
        }
        
        for btn_type, btn in buttons.items():
            if btn_type == active_type:
                btn.config(
                    bg=self.constants.COLORS['primary'],
                    fg='white',
                    relief=tk.FLAT
                )
            else:
                btn.config(
                    bg=self.constants.COLORS['bg'],
                    fg=self.constants.COLORS['text'],
                    relief=tk.RAISED
                )
    
    def toggle_automation(self):
        """Otomasyonu başlatır/durdurur"""
        is_running = self.viewmodel.toggle_automation()
        
        # Butonların durumunu güncelle
        if is_running:
            self.automation_button.config(
                text="⏹️ Otomasyonu Durdur",
                bg=self.constants.COLORS['danger']
            )
            self.pause_button.config(
                state=tk.NORMAL,
                text="⏸️ Duraklat (P)",
                bg=self.constants.COLORS['bg']
            )
        else:
            self.automation_button.config(
                text="▶️ Otomasyonu Başlat",
                bg=self.constants.COLORS['success']
            )
            self.pause_button.config(
                text="⏸️ Duraklat (P)",
                state=tk.DISABLED,
                bg=self.constants.COLORS['bg']
            )
    
    def toggle_pause(self):
        """Otomasyonu duraklatır/devam ettirir"""
        is_paused = self.viewmodel.toggle_pause()
        self.update_pause_state(is_paused)
    
    def update_pause_state(self, is_paused):
        """Duraklat butonunun durumunu günceller"""
        if is_paused:
            self.pause_button.config(
                text="▶️ Devam Et (P)",
                bg=self.constants.COLORS['success']
            )
        else:
            self.pause_button.config(
                text="⏸️ Duraklat (P)",
                bg=self.constants.COLORS['bg']
            )
    
    def add_to_queue(self):
        """Aktif seti kuyruğa ekler"""
        set_name = self.viewmodel.add_to_queue()
        if set_name:
            self.queue_listbox.insert(tk.END, set_name)
    
    def remove_from_queue(self):
        """Seçili seti kuyruktan çıkarır"""
        selection = self.queue_listbox.curselection()
        if selection:
            index = selection[0]
            if self.viewmodel.remove_from_queue(index):
                self.queue_listbox.delete(index)
    
    def add_new_set(self):
        """Yeni set ekler"""
        set_name = self.viewmodel.add_new_set()
        if set_name:
            self.add_set_button(set_name)
            self.switch_set(set_name)
    
    def add_set_button(self, set_name):
        """Set butonu ekler"""
        # Set container frame
        set_frame = ttk.Frame(self.set_buttons_frame)
        set_frame.pack(side=tk.LEFT, padx=5)
        
        # Set butonu
        set_btn = tk.Button(
            set_frame,
            text=set_name,
            command=lambda name=set_name: self.switch_set(name),
            bg=self.constants.COLORS['primary'],
            fg='white',
            font=(self.constants.STYLES['font_family'], 10),
            relief=tk.FLAT,
            width=12
        )
        set_btn.pack(side=tk.LEFT, padx=2)
        
        # Set ismi değiştirme butonu
        rename_btn = tk.Button(
            set_frame,
            text="✏️",
            command=lambda name=set_name, btn=set_btn, frame=set_frame: 
                self.rename_set(name, btn, frame),
            bg=self.constants.COLORS['bg'],
            fg=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 8),
            relief=tk.RAISED,
            width=2
        )
        rename_btn.pack(side=tk.LEFT, padx=2)
        
        # Kuyruğa ekleme butonu
        queue_btn = tk.Button(
            set_frame,
            text="➕",
            command=lambda name=set_name: self.add_set_to_queue(name),
            bg=self.constants.COLORS['bg'],
            fg=self.constants.COLORS['text'],
            font=(self.constants.STYLES['font_family'], 8),
            relief=tk.RAISED,
            width=2
        )
        queue_btn.pack(side=tk.LEFT, padx=2)
        
        self.set_buttons.append((set_frame, set_btn))
    
    def rename_set(self, old_name, button, frame):
        """Set ismini değiştirir"""
        new_name = simpledialog.askstring("Set İsmini Değiştir", 
                                        "Yeni set ismi:",
                                        initialvalue=old_name,
                                        parent=self)
        if new_name and new_name != old_name:
            if self.viewmodel.rename_set(old_name, new_name):
                # Buton metnini güncelle
                button.config(text=new_name)
                
                # Command'leri güncelle
                button.config(command=lambda: self.switch_set(new_name))
                for child in frame.winfo_children():
                    if child != button:
                        if "✏️" in str(child.cget("text")):
                            child.config(command=lambda n=new_name, b=button, f=frame: 
                                       self.rename_set(n, b, f))
                        elif "➕" in str(child.cget("text")):
                            child.config(command=lambda n=new_name: self.add_set_to_queue(n))
                
                # Kuyruk listesini güncelle
                self.update_queue_list()
            else:
                messagebox.showerror("Hata", "Set ismi değiştirilemedi!")
    
    def add_set_to_queue(self, set_name):
        """Belirli bir seti kuyruğa ekler"""
        self.viewmodel.add_set_to_queue(set_name)
        self.update_queue_list()
    
    def update_queue_list(self):
        """Kuyruk listesini günceller"""
        self.queue_listbox.delete(0, tk.END)
        for set_name in self.viewmodel.get_queue():
            self.queue_listbox.insert(tk.END, set_name)
    
    def switch_set(self, set_name):
        """Setler arası geçiş yapar"""
        if self.viewmodel.switch_set(set_name):
            # Set butonlarının görünümünü güncelle
            for frame, btn in self.set_buttons:
                if btn.cget("text") == set_name:
                    btn.config(
                        bg=self.constants.COLORS['primary'],
                        fg='white',
                        relief=tk.FLAT
                    )
                else:
                    btn.config(
                        bg=self.constants.COLORS['bg'],
                        fg=self.constants.COLORS['text'],
                        relief=tk.RAISED
                    )
            
            # UI'ı güncelle
            self.update_ui()
    
    def save_loop_count(self, event=None):
        """Döngü sayısını kaydeder"""
        try:
            count = int(self.loop_count_entry.get())
            if count > 0:
                self.viewmodel.save_loop_count(count)
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir döngü sayısı giriniz!")
            self.loop_count_entry.delete(0, tk.END)
            self.loop_count_entry.insert(0, "1")
        finally:
            self.clear_focus()
    
    def goto_coordinate(self, index):
        """Seçili koordinata gider"""
        self.viewmodel.goto_coordinate(index)
    
    def update_coordinate(self, index):
        """Seçili koordinatı günceller"""
        position = self.viewmodel.get_current_mouse_position()
        if position:
            self.viewmodel.update_coordinate_position(index, position)
            self.update_ui()
            # Sesli bildirim
            self.bell()
            # Koordinat güncellendiğinde bilgi mesajı göster
            current_pos = f"({position['x']}, {position['y']})"
            messagebox.showinfo("Koordinat Güncellendi", 
                              f"Koordinat {index + 1} güncellendi: {current_pos}")
    
    def start_edit_label(self, event, index):
        """Koordinat etiketini düzenleme moduna alır"""
        label = self.coordinates_labels[index]
        current_text = label.cget("text")
        
        # Entry widget oluştur
        entry = ttk.Entry(label.master, width=15)
        entry.insert(0, current_text)
        entry.select_range(0, tk.END)
        
        # Entry'yi konumlandır
        entry.grid(row=label.grid_info()['row'], 
                  column=label.grid_info()['column'], 
                  sticky="w")
        entry.focus_set()
        
        # Event handler'ları bağla
        entry.bind('<Return>', lambda e: self.finish_edit_label(e, index, entry))
        entry.bind('<FocusOut>', lambda e: self.finish_edit_label(e, index, entry))
        
        # Label'ı gizle
        label.grid_remove()
    
    def finish_edit_label(self, event, index, entry):
        """Koordinat etiketi düzenlemeyi bitirir"""
        new_text = entry.get()
        label = self.coordinates_labels[index]
        
        # Entry'yi kaldır ve label'ı göster
        entry.destroy()
        label.grid()
        
        # Etiketi güncelle
        if new_text:
            label.config(text=new_text)
            self.viewmodel.update_coordinate_label(index, new_text) 
    
    def update_ui(self):
        """Tüm UI elemanlarını günceller"""
        # Aktif setin verilerini al
        set_data = self.viewmodel.get_active_set_data()
        if not set_data:
            return
        
        # Döngü sayısını güncelle
        self.loop_count_entry.delete(0, tk.END)
        self.loop_count_entry.insert(0, str(set_data['loop_count']))
        
        # Koordinat verilerini güncelle
        coordinates = set_data['coordinates']
        for i in range(20):
            # Varsayılan değerler
            label_text = f"K {i+1}: "
            click_type = 'left'
            text = ''
            delay = self.constants.COORDINATES['default_delay']
            order = i
            
            # Eğer koordinat varsa değerleri al
            if i < len(coordinates):
                coord = coordinates[i]
                label_text = coord['label']
                click_type = coord['click_type']
                text = coord['text']
                delay = coord['delay']
                order = coord['order']
            
            # UI elemanlarını güncelle
            self.coordinates_labels[i].configure(text=label_text)
            self.update_click_buttons(i, click_type)
            self.text_entries[i].delete(0, tk.END)
            self.text_entries[i].insert(0, text)
            self.delay_entries[i].delete(0, tk.END)
            self.delay_entries[i].insert(0, str(delay))
            self.order_entries[i].delete(0, tk.END)
            self.order_entries[i].insert(0, str(order))
        
        # Aktif koordinatı vurgula
        if self.viewmodel.coordinate_mode_active:
            self.highlight_active_coordinate()
    
    def update_click_buttons(self, index, active_type):
        """Tıklama butonlarının görünümünü günceller"""
        buttons = {
            'left': self.left_buttons[index],
            'right': self.right_buttons[index],
            'double': self.double_buttons[index]
        }
        
        for btn_type, btn in buttons.items():
            if btn_type == active_type:
                btn.config(
                    bg=self.constants.COLORS['primary'],
                    fg='white',
                    relief=tk.FLAT
                )
            else:
                btn.config(
                    bg=self.constants.COLORS['bg'],
                    fg=self.constants.COLORS['text'],
                    relief=tk.RAISED
                )
    
    def update_coordinate_label(self, index, text=""):
        """Koordinat etiketini günceller"""
        if not text:
            text = f"K {index+1}: "
        self.coordinates_labels[index].config(text=text)
    
    # Dosya İşlemleri
    def new_file(self):
        """Yeni dosya oluşturur"""
        if messagebox.askokcancel("Yeni", "Tüm veriler silinecek. Emin misiniz?"):
            self.viewmodel.new_file()
            self.update_ui()
            
            # Set butonlarını temizle
            for btn in self.set_buttons:
                btn.destroy()
            self.set_buttons.clear()
            
            # Kuyruk listesini temizle
            self.queue_listbox.delete(0, tk.END)
    
    def open_file(self):
        """Dosya açar"""
        filename = filedialog.askopenfilename(
            title="Dosya Aç",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.viewmodel.open_file(filename):
                # Set butonlarını güncelle
                for btn in self.set_buttons:
                    btn.destroy()
                self.set_buttons.clear()
                
                # Yeni set butonlarını oluştur
                for set_name in self.viewmodel.get_set_names():
                    set_btn = tk.Button(
                        self.set_buttons_frame,
                        text=set_name,
                        command=lambda name=set_name: self.switch_set(name),
                        bg=self.constants.COLORS['bg'],
                        fg=self.constants.COLORS['text'],
                        font=(self.constants.STYLES['font_family'], 10),
                        relief=tk.RAISED,
                        width=12
                    )
                    set_btn.grid(row=0, column=len(self.set_buttons), padx=5)
                    self.set_buttons.append(set_btn)
                
                # İlk seti seç
                if self.set_buttons:
                    self.switch_set(self.set_buttons[0]['text'])
                
                # Kuyruk listesini güncelle
                self.queue_listbox.delete(0, tk.END)
                for set_name in self.viewmodel.get_queue():
                    self.queue_listbox.insert(tk.END, set_name)
            else:
                messagebox.showerror("Hata", "Dosya açılırken bir hata oluştu!")
    
    def save_file(self):
        """Dosyayı kaydeder"""
        if not self.viewmodel.has_current_file():
            self.save_as_file()
        else:
            if not self.viewmodel.save_file():
                messagebox.showerror("Hata", "Dosya kaydedilirken bir hata oluştu!")
    
    def save_as_file(self):
        """Dosyayı farklı kaydeder"""
        filename = filedialog.asksaveasfilename(
            title="Farklı Kaydet",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if not self.viewmodel.save_file_as(filename):
                messagebox.showerror("Hata", "Dosya kaydedilirken bir hata oluştu!") 
    
    def get_coordinate_data(self):
        """UI'dan koordinat verilerini toplar"""
        coordinates = []
        for i in range(20):  # 20 koordinat satırı
            try:
                coord_data = {
                    'label': self.coordinates_labels[i].cget("text"),
                    'click_type': self.get_click_type_from_buttons(i),
                    'text': self.text_entries[i].get(),
                    'delay': float(self.delay_entries[i].get() or 0.5),
                    'order': int(self.order_entries[i].get() or i),
                    'position': self.viewmodel.model.get_coordinate_position(i)
                }
                coordinates.append(coord_data)
            except Exception as e:
                print(f"Satır {i} verisi alınırken hata: {e}")
                continue
        return coordinates
    
    def get_click_type_from_buttons(self, index):
        """UI butonlarından tıklama tipini alır"""
        if self.left_buttons[index].cget("relief") == "flat":
            return "left"
        elif self.right_buttons[index].cget("relief") == "flat":
            return "right"
        elif self.double_buttons[index].cget("relief") == "flat":
            return "double"
        return "left"  # Varsayılan 
    
    def save_current_set_data(self, event=None):
        """Mevcut set verilerini kaydeder"""
        self.viewmodel.save_current_set_data() 