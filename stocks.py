import customtkinter as ctk
from settings import *
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass


# StockMarketApp class definition
class StockMarketApp(ctk.CTk):
    def __init__(self):
        # Initialize the main application window
        super().__init__(fg_color=BG_COLOR)
        self.geometry('900x800')
        self.title('')
        self.iconbitmap('empty.ico')
        self.title_bar_color()

        # Initialize data variables
        self.input_string = ctk.StringVar(value='AMZN')
        self.time_string = ctk.StringVar(value=TIME_OPTIONS[0])
        self.time_string.trace('w', self.create_graph)
        self.has_data = False

        # Initialize widgets and UI components
        self.graph_panel = None
        InputPanel(self, self.input_string, self.time_string)

        # Bind event handler for Enter key
        self.bind('<Return>', self.input_handler)

        # Start the main event loop
        self.mainloop()

    def create_graph(self, *args):
        # Remove the existing graph panel if it exists
        if self.graph_panel:
            self.graph_panel.pack_forget()

        # Create a new graph panel based on the selected time option
        if self.has_data:
            match self.time_string.get():
                case 'Max':
                    data = self.max
                case '1 Year':
                    data = self.year
                case '6 Months':
                    data = self.six_months
                case 'Month':
                    data = self.one_month
                case 'Week':
                    data = self.one_week

            self.graph_panel = GraphPanel(self, data)

    def input_handler(self, event=None):
        # Handle user input for stock symbol and fetch corresponding data
        ticker = yf.Ticker(self.input_string.get())
        start = datetime(1950, 1, 1)
        end = datetime.today()

        # Retrieve historical stock data for different time periods
        self.max = ticker.history(start=start, end=end, period='1d')
        self.year = self.max.iloc[-260:]
        self.six_months = self.max.iloc[-130:]
        self.one_month = self.max.iloc[-22:]
        self.one_week = self.max.iloc[-5:]
        self.has_data = True

        # Update the graph based on the new data
        self.create_graph()

    def title_bar_color(self):
        # Set the color of the title bar
        try:
            HWND = windll.user32.GetParent(self.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(TITLE_HEX_COLOR)), sizeof(c_int))
        except:
            pass


# InputPanel class definition
class InputPanel(ctk.CTkFrame):
    def __init__(self, parent, input_string, time_string):
        # Initialize the input panel frame
        super().__init__(master=parent, fg_color=INPUT_BG_COLOR, corner_radius=0)
        self.pack(fill='both', side='bottom')

        # Create and pack the stock symbol entry widget
        ctk.CTkEntry(self, textvariable=input_string, fg_color=TEXT_INPUT_BG_COLOR, border_color=TEXT_INPUT_BG_COLOR,
                     border_width=1).pack(
            side='left', padx=10, pady=10)

        # Create and initialize time selection buttons
        self.buttons = [TextButton(self, text, time_string) for text in TIME_OPTIONS]

        # Set up a trace to unselect buttons when the time option changes
        time_string.trace('w', self.unselect_all_buttons)

    def unselect_all_buttons(self, *args):
        # Unselect all time selection buttons
        for button in self.buttons:
            button.unselect()


# TextButton class definition
class TextButton(ctk.CTkLabel):
    def __init__(self, parent, text, time_string):
        # Initialize the text button
        super().__init__(master=parent, text=text, text_color=TEXT_COLOR)
        self.pack(side='right', padx=10, pady=10)
        self.bind('<Button>', self.select_handler)

        # Store references to time_string and text
        self.time_string = time_string
        self.text = text

        # Auto-select the button if it matches the current time option
        if time_string.get() == text:
            self.select_handler()

    def select_handler(self, event=None):
        # Handle button selection and update the time_string variable
        self.time_string.set(self.text)
        self.configure(text_color=HIGHLIGHT_COLOR)

    def unselect(self):
        # Unselect the button by resetting its text color
        self.configure(text_color=TEXT_COLOR)


# GraphPanel class definition
class GraphPanel(ctk.CTkFrame):
    def __init__(self, parent, data):
        # Initialize the graph panel frame
        super().__init__(master=parent, fg_color=BG_COLOR)
        self.pack(expand=True, fill='both')

        # Create a matplotlib figure and set up the graph
        figure = plt.Figure()
        figure.subplots_adjust(left=0, right=0.99, bottom=0, top=1)
        figure.patch.set_facecolor(BG_COLOR)

        ax = figure.add_subplot(111)
        ax.set_facecolor(BG_COLOR)

        # Customize the appearance of the graph
        for side in ['top', 'left', 'right', 'bottom']:
            ax.spines[side].set_color(BG_COLOR)

        line = ax.plot(data['Close'])[0]
        line.set_color(HIGHLIGHT_COLOR)

        # Customize tick parameters
        ax.tick_params(axis='x', direction='in', pad=-14, colors=TICK_COLOR)
        ax.yaxis.tick_right()
        ax.tick_params(axis='y', direction='in', pad=-22, colors=HIGHLIGHT_COLOR)

        # Create a FigureCanvasTkAgg widget to embed the graph in the GUI
        figure_widget = FigureCanvasTkAgg(figure, master=self)
        figure_widget.get_tk_widget().pack(fill='both', expand=True)


# Start the StockMarketApp
StockMarketApp()
