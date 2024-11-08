# button_functions.py
from PyQt5.QtWidgets import QColorDialog
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import datetime



def increase_speed(UI_MainWindow, isLinked, graphNum):
    if isLinked:
        current_interval = UI_MainWindow.timer_linked_graphs.interval()  # Get the current interval in milliseconds
        if current_interval > 100:  # Prevent it from going too fast
            new_interval = max(100, current_interval - 100)  # Decrease the interval to make it faster
            UI_MainWindow.timer_linked_graphs.setInterval(new_interval)
            UI_MainWindow.timer_graph_1.setInterval(new_interval)
            UI_MainWindow.timer_graph_2.setInterval(new_interval)

            print(f"Speed increased. New interval: {new_interval} ms")
    else:
        if graphNum == 1:
            current_interval = UI_MainWindow.timer_graph_1.interval()  # Get the current interval in milliseconds
            if current_interval > 100:  # Prevent it from going too fast
                new_interval = max(100, current_interval - 100)  # Decrease the interval to make it faster
                UI_MainWindow.timer_graph_1.setInterval(new_interval)
                print(f"Speed increased. New interval: {new_interval} ms")
        else:
            current_interval = UI_MainWindow.timer_graph_2.interval()  # Get the current interval in milliseconds
            if current_interval > 100:  # Prevent it from going too fast
                new_interval = max(100, current_interval - 100)  # Decrease the interval to make it faster
                UI_MainWindow.timer_graph_2.setInterval(new_interval)
                print(f"Speed increased. New interval: {new_interval} ms")



def decrease_speed(UI_MainWindow, isLinked, graphNum):
    if isLinked:
        current_interval = UI_MainWindow.timer_linked_graphs.interval()  # Get the current interval in milliseconds
        new_interval = current_interval + 100  # Increase the interval to make it slower
        UI_MainWindow.timer_linked_graphs.setInterval(new_interval)
        UI_MainWindow.timer_graph_1.setInterval(new_interval)
        UI_MainWindow.timer_graph_2.setInterval(new_interval)
        print(f"Speed decreased. New interval: {new_interval} ms")
    else:
        if graphNum == 1:
            current_interval = UI_MainWindow.timer_graph_1.interval()  # Get the current interval in milliseconds
            new_interval = current_interval + 100  # Increase the interval to make it slower
            UI_MainWindow.timer_graph_1.setInterval(new_interval)
            print(f"Speed decreased. New interval: {new_interval} ms")
        else:
            current_interval = UI_MainWindow.timer_graph_2.interval()  # Get the current interval in milliseconds
            new_interval = current_interval + 100  # Increase the interval to make it slower
            UI_MainWindow.timer_graph_2.setInterval(new_interval)
            print(f"Speed decreased. New interval: {new_interval} ms")



def start_simulation(UI_MainWindow, isLinked, graphNum):
    if isLinked:
        if not UI_MainWindow.timer_linked_graphs.isActive():
            UI_MainWindow.timer_linked_graphs.start()
            UI_MainWindow.timer_graph_1.start()
            UI_MainWindow.timer_graph_2.start()
            # Update limits for linked graphs (if needed)

        else:
            UI_MainWindow.timer_linked_graphs.stop()
            UI_MainWindow.timer_graph_1.stop()
            UI_MainWindow.timer_graph_2.stop()
            # Update limits for linked graphs (if needed)

    
    else:
        if graphNum == 1:
            if not UI_MainWindow.timer_graph_1.isActive():
                UI_MainWindow.timer_graph_1.start()
            else:
                UI_MainWindow.timer_graph_1.stop()
        else:
            if not UI_MainWindow.timer_graph_2.isActive():
                UI_MainWindow.timer_graph_2.start()
            else:
                UI_MainWindow.timer_graph_2.stop()

    UI_MainWindow.toggleIcons(isLinked , graphNum)


def stop_simulation(UI_MainWindow, isLinked, graphNum):
    if isLinked:
        if  UI_MainWindow.timer_linked_graphs.isActive():
            UI_MainWindow.timer_linked_graphs.stop()
            UI_MainWindow.timer_graph_1.stop()
            UI_MainWindow.timer_graph_2.stop()
        else:
            UI_MainWindow.timer_graph_1.start()
            UI_MainWindow.timer_graph_2.start()
            UI_MainWindow.timer_linked_graphs.start()
    else:
        if graphNum == 1:
            if  UI_MainWindow.timer_graph_1.isActive():
                UI_MainWindow.timer_graph_1.stop()
            else:
                UI_MainWindow.timer_graph_1.start()

        else:
            if  UI_MainWindow.timer_graph_2.isActive():
                UI_MainWindow.timer_graph_2.stop()
            else:
                UI_MainWindow.timer_graph_2.start()


def rewind(UI_MainWindow, isLinked , graphNum):
    # clear the graph
    if isLinked:
        UI_MainWindow.graph1.clear()
        UI_MainWindow.graph2.clear()
        if UI_MainWindow.timer_linked_graphs.isActive():
            UI_MainWindow.timer_linked_graphs.stop()  # Stop the timer if it's running
            UI_MainWindow.timer_graph_1.stop()
            UI_MainWindow.timer_graph_2.stop()

        UI_MainWindow.time_index_linked_graphs = 0  # Reset the time index to the beginning
        # Start the simulation again from the beginning
        UI_MainWindow.timer_linked_graphs.start()
        UI_MainWindow.timer_graph_1.start()
        UI_MainWindow.timer_graph_2.start()
    else:
        if graphNum == 1:
            UI_MainWindow.graph1.clear()
            if UI_MainWindow.timer_graph_1.isActive():
                UI_MainWindow.timer_graph_1.stop()
            UI_MainWindow.time_index_graph_1 = 0
            UI_MainWindow.timer_graph_1.start()     
        else:
            UI_MainWindow.graph2.clear()
            if UI_MainWindow.timer_graph_2.isActive():
                UI_MainWindow.timer_graph_2.stop()
            UI_MainWindow.time_index_graph_2 = 0
            UI_MainWindow.timer_graph_2.start()     



def change_color(UI_MainWindow, isLinked ,graphNum):
    # open a color dialog to choose a color
    color = QColorDialog.getColor()
    if isLinked:
        if color.isValid():
            print("Color Has Been Changed")
            UI_MainWindow.linked_graphs_color = color.name()
            print(f"It Becomes: {UI_MainWindow.linked_graphs_color}")
    else:

        if color.isValid():
            if graphNum == 1:
                UI_MainWindow.graph1_color  = color.name()
            else:
                UI_MainWindow.graph2_color = color.name()



def setup_graph_widget(graph_widget):
    graph_widget.setMouseEnabled(x=True, y=True)
    graph_widget.showGrid(x=True, y=True)
    graph_widget.addLegend()


def update_graph_data(graph_widget, x_data, y_data, pen='r'):
    graph_widget.clear()
    graph_widget.plot(x_data, y_data, pen=pen)





def capture_signal_screenshot(graph_widget):
    """Capture a screenshot of the signal plot and save it as an image."""
    img_path = f"signal_screenshot_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    
    # Grab the widget's content
    screenshot = graph_widget.grab()
    
    # Save the screenshot to a file
    screenshot.save(img_path, "PNG")
    
    return img_path





def export_to_pdf(UI_MainWindow, isLinked, graphNum):
    # Create a PDF document
    report_name = f"Signal_Report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    pdf = SimpleDocTemplate(report_name, pagesize=A4)

    elements = []

    title = Paragraph(f"<b>Signal Report</b>", getSampleStyleSheet()['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    if isLinked:
        elements.append(Paragraph(f"<b>Linked Graphs Report</b>", getSampleStyleSheet()['Heading2']))
        elements.append(Paragraph(f"<b>Graph 1 Signal Report</b>", getSampleStyleSheet()['Heading2']))
        img1_path = capture_signal_screenshot(UI_MainWindow.graph1)  # Use the correct attribute
        elements.append(Image(img1_path, width=400, height=200))
        elements.append(create_stats_table(UI_MainWindow.loadSignalData(UI_MainWindow.graph_1_files[-1]), "Graph 1 Signal"))
        elements.append(Paragraph(f"<b>Graph 2 Signal Report</b>", getSampleStyleSheet()['Heading2']))
        img2_path = capture_signal_screenshot(UI_MainWindow.graph2)  # Use the correct attribute
        elements.append(Image(img2_path, width=400, height=200))
        elements.append(create_stats_table(UI_MainWindow.loadSignalData(UI_MainWindow.graph_2_files[-1]), "Graph 2 Signal"))

    else:
        if graphNum == 1:
            elements.append(Paragraph(f"<b>Graph 1 Signal Report</b>", getSampleStyleSheet()['Heading2']))
            img1_path = capture_signal_screenshot(UI_MainWindow.graph1)  # Use the correct attribute
            elements.append(Image(img1_path, width=400, height=200))
            elements.append(create_stats_table(UI_MainWindow.loadSignalData(UI_MainWindow.graph_1_files[-1]), "Graph 1 Signal"))
        else:
            elements.append(Paragraph(f"<b>Graph 2 Signal Report</b>", getSampleStyleSheet()['Heading2']))
            img2_path = capture_signal_screenshot(UI_MainWindow.graph2)  # Use the correct attribute
            elements.append(Image(img2_path, width=400, height=200))
            elements.append(create_stats_table(UI_MainWindow.loadSignalData(UI_MainWindow.graph_2_files[-1]), "Graph 2 Signal"))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", getSampleStyleSheet()['Normal']))

    pdf.build(elements)
    print(f"Report generated: {report_name}")




def export_to_pdf_glued(glued_graph, glued_data):
    # Create a PDF document
    report_name = f"Signal_Report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    pdf = SimpleDocTemplate(report_name, pagesize=A4)

    elements = []

    title = Paragraph(f"<b>Signal Report</b>", getSampleStyleSheet()['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Graph 1 Signal Report</b>", getSampleStyleSheet()['Heading2']))
    img1_path = capture_signal_screenshot(glued_graph)  # Use the correct attribute
    elements.append(Image(img1_path, width=400, height=200))
    elements.append(create_stats_table(glued_data, "Graph 1 Signal"))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", getSampleStyleSheet()['Normal']))

    pdf.build(elements)
    print(f"Report generated: {report_name}")

def create_stats_table(signal_data, graph_label):
    """Create a table for signal statistics such as mean, std, min, max, and duration."""
    
    if signal_data is None:
        return Paragraph(f"No data available for {graph_label}", getSampleStyleSheet()['Normal'])
    
    # Calculate statistics
    mean_val = np.mean(signal_data)
    std_val = np.std(signal_data)
    min_val = np.min(signal_data)
    max_val = np.max(signal_data)
    duration = len(signal_data)  # Assuming each point represents a time unit

    # Create a table with stats
    data = [
        ["Statistic", "Value"],
        ["Mean", f"{mean_val:.2f}"],
        ["Standard Deviation", f"{std_val:.2f}"],
        ["Min Value", f"{min_val:.2f}"],
        ["Max Value", f"{max_val:.2f}"],
        ["Duration", f"{duration} points"]
    ]


    # Format the table
    table = Table(data, colWidths=[250, 150])  # Set column widths to fit within the PDF layout
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align all cells to center
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Background for body
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid
        ('TOPPADDING', (0, 0), (-1, -1),10),  # Add padding above the table
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),  # Add padding below the table
    ]))

    return table




# Define the function to remove a signal from the graph
def remove_signal(UI_MainWindow, isLinked, graphNum, SelectedFile):
    if graphNum == 1:
        remove_signal_from_graph(UI_MainWindow, isLinked, 1 ,SelectedFile)
    else:
        remove_signal_from_graph(UI_MainWindow, isLinked, 2 ,SelectedFile)


def remove_signal_from_graph(UI_MainWindow, isLinked, graphNum, selectedFile):
    if isLinked:
        for i, signal in enumerate(UI_MainWindow.graph_1_files):
            if signal == selectedFile:
                UI_MainWindow.graph_1_files.pop(i)
        for i, signal in enumerate(UI_MainWindow.graph_2_files):
            if signal == selectedFile:
                UI_MainWindow.graph_2_files.pop(i)
        
        rewind(UI_MainWindow, isLinked,  graphNum)
        if len(UI_MainWindow.graph_1_files) == 0 or len(UI_MainWindow.graph_2_files) == 0:  
            stop_simulation(UI_MainWindow, isLinked,  graphNum)
    
    else:
        if graphNum == 1:
            for i, signal in enumerate(UI_MainWindow.graph_1_files):
                if signal == selectedFile:
                    UI_MainWindow.graph_1_files.pop(i)
            
            rewind(UI_MainWindow, isLinked,  graphNum)
            if len(UI_MainWindow.graph_1_files) == 0:
                stop_simulation(UI_MainWindow, isLinked,  graphNum)
        else:
            for i, signal in enumerate(UI_MainWindow.graph_2_files):
                if signal == selectedFile:
                    UI_MainWindow.graph_2_files.pop(i)
            
            rewind(UI_MainWindow, isLinked,  graphNum)
            if len(UI_MainWindow.graph_2_files) == 0:
                stop_simulation(UI_MainWindow, isLinked,  graphNum)


def remove_linked_signals(UIMainWindow):
    UIMainWindow.graph_1_files = [] 
    UIMainWindow.graph_2_files = []
    UIMainWindow.graph1_colors= []
    UIMainWindow.graph2_colors = []
    UIMainWindow.fileListWidgetGraph1.clear()
    UIMainWindow.fileListWidgetGraph2.clear()
    UIMainWindow.graph1.clear()
    UIMainWindow.graph2.clear()
    UIMainWindow.timer_linked_graphs.stop()
    UIMainWindow.timer_graph_1.stop()
    UIMainWindow.timer_graph_2.stop()