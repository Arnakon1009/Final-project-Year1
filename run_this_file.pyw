import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import json
from PIL import Image, ImageTk
import ctypes
from dotenv import load_dotenv

#Setup
try:
    myappid = 'Pleang Sakoon Ngern.app.1.0' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

load_dotenv()

#Data & Constant Value
currency_list = [
    "USD", "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", 
    "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", 
    "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLF", 
    "CLP", "CNH", "CNY", "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", 
    "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", 
    "GEL", "GGP", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", 
    "HRK", "HTG", "HUF", "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", 
    "JEP", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KID", "KMF", "KRW", 
    "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", 
    "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", 
    "MXN", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", 
    "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", 
    "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", 
    "SLL", "SOS", "SRD", "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", 
    "TND", "TOP", "TRY", "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "UYU", 
    "UZS", "VES", "VND", "VUV", "WST", "XAF", "XCD", "XCG", "XDR", "XOF", 
    "XPF", "YER", "ZAR", "ZMW", "ZWG", "ZWL"
]

theme = [
    "light", "dark"
]

colors_list = [
    "black", "white", "blue", "green", "red", "gold", "snow",
    "mediumblue", "darkgreen", "orange", "purple", "gray", "whitesmoke", 
    "navy", "forestgreen", "darksalmon", "violet", "lightgray", "gainsboro", 
    "dodgerblue", "seagreen", "tomato", "magenta", "dimgray", "linen", 
    "lightskyblue", "palegreen", "pink", "brown", "antiquewhite", 
    "turquoise", "limegreen", "crimson", "chocolate", "bisque", "cyan", 
    "yellowgreen", "maroon", "beige", "cornsilk", "cadetblue", 
    "darkolivegreen", "indianred", "khaki"
]

SETTING_FILE =  "settings.json"

DEFAULT_SETTING  = {
    "theme_checklist" : 1,
    "theme" : "light",
    "theme_color" : "snow",
    "text_color" : "black",
    "krapao_value" : 57.0,
    "krapao_unit" : "THB"
}

#API Handling
api_cache = {}

def call_api_rate(from_curr, to_curr):
    #Error handle
    if from_curr not in currency_list:
        messagebox.showerror("Data Error", "Not valid currency value")
        return
    if to_curr not in currency_list:
        messagebox.showerror("Data Error", "Not valid currency value")
        return
    
    if from_curr == to_curr:
        return 1.0
    
    if from_curr in api_cache:
        if to_curr in api_cache[from_curr]:
            return api_cache[from_curr][to_curr]
    
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        messagebox.showerror("Error", "Not found api key!")
        return None
    
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_curr}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data["result"] == "success":
            #Keep data in cache
            conversion_rates = data["conversion_rates"]
            api_cache[from_curr] = conversion_rates
            #Return rate for another use
            return conversion_rates.get(to_curr)
        else:
            return "Error: fetching data. Please try again."
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error","Connection lost.")
    except requests.exceptions.Timeout:
        messagebox.showwarning("Connection Error", "Timeout. Please try again.")
    except Exception as e:
        messagebox.showerror(f"Unexpected Error",f"{str(e)}")

#Logic functions
def convert_currency():
    try:
        amt = float(amount.get())
        f_curr = from_curr.get().upper()
        t_curr = to_curr.get().upper()
        
        if not f_curr or not t_curr:
            return

        rate = call_api_rate(f_curr, t_curr)

        if rate is not None:
            value = amt*rate
            result_text_value.config(text=f"{value:.2f} in {t_curr}")

    except ValueError:
        result_text_value.config(text="Error: Please enter a number.")

def convert_kaprao(value, from_curr):
    base_unit = setting_value.get("krapao_unit", "THB")

    rate_unit_to_thb = call_api_rate(base_unit, "THB")
    if rate_unit_to_thb is None: return None
    
    krapao_price_thb = setting_value.get("krapao_value", 57) * rate_unit_to_thb

    rate_money_to_thb = call_api_rate(from_curr, "THB")
    if rate_money_to_thb is None: return None
    
    user_money_thb = value * rate_money_to_thb

    if krapao_price_thb == 0: return {"result": 0, "unit": "plate"} # กัน error หารด้วย 0
    
    result = int(user_money_thb / krapao_price_thb)
    unit = "plates" if result > 1 else "plate"
    
    return {"result": result, "unit": unit}

def call_kaprao():
    try:
        value = float(value_entry.get())
        from_curr = value_combo.get().upper()
        if not from_curr: return

        data = convert_kaprao(value, from_curr)
        if data:
            Krapao_value_label.config(text=data["result"])
            Krapao_unit_label.config(text=data["unit"])
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount.")

def clear_kaprao():
    value_entry.delete(0, tk.END)
    value_combo.set("")
    Krapao_value_label.config(text="")
    Krapao_unit_label.config(text="")

#Setting & UI Logic
def load_setting():
    if os.path.exists(SETTING_FILE):
        try :
            with open(SETTING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_SETTING.copy()

setting_value = load_setting()

def update_all_widgets_color(bg, fg):
    root.configure(background=bg)
    def apply_to_all(window):
        for widget in window.winfo_children():
            if isinstance(widget, (ttk.Label, tk.Label)):
                widget.configure(background=bg, foreground=fg)
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(
                    background=bg, 
                    foreground=fg,
                    activebackground=bg, 
                    activeforeground=fg,
                    selectcolor=bg,
                    highlightbackground=bg
                )
            elif isinstance(widget, (ttk.Entry, ttk.Combobox, tk.Entry)):
                entry_bg = "white" if bg == "snow" else "#f0f0f0"
                dark_text = "black"
                try:
                    if isinstance(widget, (tk.Entry, ttk.Entry)):
                        widget.configure(background=entry_bg, foreground=dark_text)
                    elif isinstance(widget, ttk.Combobox):
                        widget.configure(foreground=dark_text)
                except:
                    pass
            elif isinstance(widget, tk.Toplevel):
                widget.configure(background=bg)
                apply_to_all(widget)
    apply_to_all(root)

def save_setting():
    try:
        if un.get() not in currency_list:
            messagebox.showerror("Error", "Currency Value is not valid.")
            return
        
        is_theme_mode = Theme_mode_var.get()
        if is_theme_mode == 1:
            if Tbox.get() == "dark":
                final_bg, final_fg = "gray20", "white"
            else:
                final_bg, final_fg = "snow", "black"
        else:
            final_bg = Bbox.get()
            final_fg = Xbox.get()
        if (final_bg not in colors_list or final_fg not in colors_list) and final_bg != "gray20":
            messagebox.showerror("Error", "Unknown Colors")
            return
        new_setting = {
            "theme_checklist": Theme_mode_var.get(),
            "theme": Tbox.get(),
            "theme_color": final_bg,
            "text_color": final_fg,
            "krapao_value": float(KP.get()),
            "krapao_unit": un.get()
        }

        with open(SETTING_FILE, "w") as f:
            json.dump(new_setting, f, indent=4)
        
        global setting_value
        setting_value = new_setting
        update_all_widgets_color(final_bg, final_fg)
        messagebox.showinfo("Saved", "Data Saved.")

    except ValueError :
        messagebox.showerror("ValueError", "Please input number")

def default_setting():
    if messagebox.askyesno("Reset", "Reset to default settings?"):
        with open(SETTING_FILE, "w") as f:
            json.dump(DEFAULT_SETTING, f, indent=4)
        global setting_value
        setting_value = DEFAULT_SETTING.copy()

        bg = setting_value.get("theme_color")
        fg = setting_value.get("text_color")
        update_all_widgets_color(bg, fg)
        refresh_setting_ui()
        messagebox.showinfo("Cleared", "Data Saved.")

def refresh_setting_ui():
    Theme_mode_var.set(setting_value.get("theme_checklist"))
    Tbox.set(setting_value.get("theme", "light"))
    Bbox.set(setting_value.get("theme_color", "snow"))
    Xbox.set(setting_value.get("text_color", "black"))
    
    KP.delete(0, tk.END)
    KP.insert(0, setting_value.get("krapao_value", 57))
    un.set(setting_value.get("krapao_unit", "THB"))
    toggle_combobox()

def clear_main():
    result_text_value.config(text="")
    amount.delete(0,tk.END)
    from_curr.set("")
    to_curr.set("")

def toggle_combobox():
    if Theme_mode_var.get() == 1:
        Bbox.config(state="disabled")
        Xbox.config(state="disabled")
        Tbox.config(state="readonly")
    else:
        Bbox.config(state="readonly")
        Xbox.config(state="readonly")
        Tbox.config(state="disabled")

#GUI Toplevel Setup
def setting_window():
    setting_ui = tk.Toplevel(root)
    setting_ui.title("Settings")
    setting_ui.geometry("400x300")
    setting_ui.resizable(width = 0, height = 0)
    try:
        setting_ui.iconbitmap(icon)
    except:
        pass
    
    #Global variable
    global Theme_mode_var, Tbox, Bbox, Xbox, KP, un

    #Theme
    Theme_mode_var = tk.IntVar(value=setting_value.get("theme_checklist"))
    Theme = tk.Checkbutton (setting_ui, text="Theme Color" ,variable=Theme_mode_var, onvalue=1, offvalue=0,background=setting_value.get("theme_color", "snow"), foreground=setting_value.get("text_color", "black"), command=toggle_combobox)
    Theme.grid(row=0,column=0 , padx= 30, pady =25)
    
    Tbox = ttk.Combobox(setting_ui,values=theme,width=15)
    Tbox.grid(row=0, column=1)

    #BG and text
    Back_ground = tk.Label (setting_ui, text="Background Color :" ,font=('Times New Roman', 14),background=setting_value.get("theme_color", "snow"), foreground=setting_value.get("text_color", "black"))
    Back_ground.grid(row=2,column=0 , padx= 30 , pady = 15)
    
    Bbox = ttk.Combobox(setting_ui,values=colors_list,width=15, foreground=setting_value.get("text_color", "black"))
    Bbox.grid(row=2, column=1)

    Text = tk.Label (setting_ui, text="Text Color :" ,font=('Times New Roman', 14),background=setting_value.get("theme_color", "snow"), foreground=setting_value.get("text_color", "black"))
    Text.grid(row=3,column=0 , padx= 30 , pady = 15)
    
    Xbox = ttk.Combobox(setting_ui,values=colors_list,width=15, foreground=setting_value.get("text_color", "black"))
    Xbox.grid(row=3, column=1)

    #Kaprao zone
    Kaprao = tk.Label (setting_ui, text="Kaprao unit  :" ,font=('Times New Roman', 14),background=setting_value.get("theme_color", "snow"), foreground=setting_value.get("text_color", "black"))
    Kaprao.grid(row=4,column=0 , padx= 30 , pady = 15)
    
    KP = ttk.Entry(setting_ui,width=15, foreground=setting_value.get("text_color", "black"))
    KP.place(x=220,y = 210)
    
    un = ttk.Combobox(setting_ui,values=currency_list,width=5, foreground=setting_value.get("text_color", "black"))
    un.place(x=325,y=210)

    #Button
    Back = ttk.Button(setting_ui,text="Back", command=setting_ui.destroy).place(x=70,y=250)
    Apply = ttk.Button(setting_ui,text="Apply", command=save_setting).place(x=160,y=250)
    Clear = ttk.Button(setting_ui,text="Clear", command=default_setting).place(x=250,y=250)

    update_all_widgets_color(setting_value.get("theme_color", "snow"), setting_value.get("text_color", "black"))
    refresh_setting_ui()

def kaprao_window():
    kaprao_ui = tk.Toplevel(root)
    kaprao_ui.title("Kaprao")
    kaprao_ui.geometry("400x350")
    kaprao_ui.resizable(width = 0, height = 0)
    try:
        kaprao_ui.iconbitmap(icon)
    except:
        pass

    #label
    Amount_label = ttk.Label(kaprao_ui, text="Amount", font=("Times New Roman", 24),background=setting_value.get("theme_color", "snow"), foreground=setting_value.get("text_color", "black"))
    Amount_label.grid(column=0,row=0,padx=15,pady=20)

    labee = ttk.Label(kaprao_ui, text="↓↓", font=("Times New Roman", 24), background=setting_value.get("theme_color", "snow"), foreground=setting_value.get("text_color", "black"))
    labee.place(x=247, y=70)

    Krapao_label = ttk.Label(kaprao_ui, text="Krapao", font=("Times New Roman", 24), background=setting_value.get("theme_color", "snow"), foreground=setting_value.get("text_color", "black"))
    Krapao_label.grid(column=0,row=1,padx=15,pady=55)

    #button
    Convert_button = ttk.Button(kaprao_ui, text="Convert", padding=9, command=call_kaprao)
    Convert_button.place(x=160, y=210)

    clear_button = ttk.Button(kaprao_ui, text="Clear", padding=9, command= clear_kaprao)
    clear_button.place(x=260, y=210)

    global value_entry, value_combo, Krapao_value_label, Krapao_unit_label

    #Input
    value_entry = ttk.Entry(kaprao_ui, width=15, foreground=setting_value.get("text_color", "black"))
    value_entry.grid(column=1, row=0, padx=15)

    value_combo = ttk.Combobox(kaprao_ui, width=8, foreground=setting_value.get("text_color", "black"), values=currency_list)
    value_combo.grid(column=2, row=0, padx=25)

    #Output
    Krapao_value_label = ttk.Label(kaprao_ui,width=15, foreground=setting_value.get("text_color", "black"), font=("Times New Roman", 15))
    Krapao_value_label.place(x=170, y= 145)

    Krapao_unit_label = ttk.Label(kaprao_ui, width=12, foreground=setting_value.get("text_color", "black"),font=("Times New Roman", 15))
    Krapao_unit_label.place(x=290, y= 145)

    #Image
    try:
        image_path = "kaprao.png" 
        pil_image = Image.open(image_path)
        pil_image.thumbnail((100, 100),Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        image_label = tk.Label(kaprao_ui, image=tk_image, width=100, height=100, background=setting_value.get("theme_color", "snow"))
        image_label.image = tk_image
        image_label.configure(image=tk_image)
        image_label.place(x=20, y=180)
    except:
        pass

    update_all_widgets_color(setting_value.get("theme_color", "snow"), setting_value.get("text_color", "black"))

def about():
    messagebox.showinfo("About", "Project Pleang Sakoon Ngern APP v1.0")

#Main window
root = tk.Tk()
root.title("Pleang Sakoon Ngern")
root.geometry("600x450+450+180")
root.resizable(width = 0, height = 0)

#Icon app
try:
    icon = "icon.ico"
    root.iconbitmap(icon)
except:
    pass

#Text and ComboBox
amount_text = ttk.Label(root, font=('Times New Roman', 25), foreground=setting_value.get("text_color", "black"), text="Amount :", background=setting_value.get("theme_color", "snow"))
amount_text.grid(row=0, column=0, padx=80, pady=25)

curr_text = ttk.Label(root, font=('Times New Roman', 25), foreground=setting_value.get("text_color", "black"), text="Currency :", background=setting_value.get("theme_color", "snow"))
curr_text.grid(row=1, column=0)

from_curr = ttk.Combobox(root,values=currency_list,width=15)
from_curr.grid(row=1, column=1)

to_text = ttk.Label(root, font=('Times New Roman', 25), foreground=setting_value.get("text_color", "black"), text="to", background=setting_value.get("theme_color", "snow"))
to_text.grid(row=2, column=1, pady=10)

to_curr = ttk.Combobox(root,values=currency_list,width=15, foreground=setting_value.get("text_color", "black"))
to_curr.grid(row=3, column=1)

result_text1 = ttk.Label(root, font=('Times New Roman', 25), foreground=setting_value.get("text_color", "black"), text="Result :", background=setting_value.get("theme_color", "snow"))
result_text1.grid(row=5, column=0)

result_text_value = ttk.Label(root, font=('Times New Roman', 15), foreground=setting_value.get("text_color", "black"), background=setting_value.get("theme_color", "snow"))
result_text_value.grid(row=5, column=1)

#entry
amount = ttk.Entry(root, font=('Times New Roman', 14), foreground=setting_value.get("text_color", "black"), width=15)
amount.grid(row=0, column=1, pady=10, padx=50)

#button
result_button = ttk.Button(root, text="Result ", padding=10, command=convert_currency)
result_button.grid(row=4, column=1, pady=20)

clear_button = ttk.Button(root, text="clear", padding=10, command=clear_main)
clear_button.grid(row=6,column=1,pady=20)

#Image
try:
    image_path = "67.png" 
    pil_image = Image.open(image_path)
    pil_image.thumbnail((150, 150),Image.Resampling.LANCZOS)
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label = tk.Label(root, image=tk_image, width=100, height=100)
    image_label.image = tk_image
    image_label.configure(image=tk_image)
    image_label.place(x=90, y=160)
except:
    pass

#Menu
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar,tearoff=0)
feauturemenu = tk.Menu(menubar, tearoff=0)

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Feauture", menu=feauturemenu)
filemenu.add_command(label="About", command=about)
filemenu.add_command(label="Setting", command=setting_window)
filemenu.add_command(label="Quit", command=root.destroy)

feauturemenu.add_command(label="Kaprao Unit", command=kaprao_window)
root.config(menu=menubar)

update_all_widgets_color(setting_value.get("theme_color", "snow"), setting_value.get("text_color", "black"))

root.mainloop()