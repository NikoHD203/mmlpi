from tkinter import *
import time
import _thread

def tempmonUI():
    w = Tk()
    w.title('Monitor')
    w.resizable(False, False)
    
    l1 = Label(w, text='Temp: ')
    l1.config(font=("Courier", 20))
    l1.grid(row=0, column=0)
    temp = StringVar()
    l2 = Label(w, textvariable=temp)
    l2.config(font=("Courier Bold", 20))
    l2.grid(row=0, column=1)
    l3 = Label(w, text='Freq: ')
    l3.config(font=("Courier", 20))
    l3.grid(row=1, column=0)
    freq = StringVar()
    l4 = Label(w, textvariable=freq)
    l4.config(font=("Courier Bold", 20))
    l4.grid(row=1, column=1)
    l5 = Label(w, text='GPU Freq: ')
    l5.config(font=("Courier", 20))
    l5.grid(row=2, column=0)
    gpufreq = StringVar()
    l6 = Label(w, textvariable=gpufreq)
    l6.config(font=("Courier Bold", 20))
    l6.grid(row=2, column=1)
    l7 = Label(w, text='Volts: ')
    l7.config(font=("Courier", 20))
    l7.grid(row=3, column=0)
    volt = StringVar()
    l8 = Label(w, textvariable=volt)
    l8.config(font=("Courier Bold", 20))
    l8.grid(row=3, column=1)

    def _update():
        while 1:
            try:
                import vcgencmd
            except Exception:
                break
            temp.set(str(vcgencmd.measure_temp()) + '°C')
            freq.set(str(round(vcgencmd.measure_clock('arm')/1000000)) + 'MHz')
            gpufreq.set(str(round(vcgencmd.measure_clock('v3d')/1000000)) + 'MHz')
            volt.set(str(round(vcgencmd.measure_volts('core'), 2)) + 'V')
            time.sleep(1)

    _thread.start_new_thread(_update, ())
    w.mainloop()

tempmonUI()