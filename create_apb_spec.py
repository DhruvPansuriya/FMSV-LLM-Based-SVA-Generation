from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_apb_spec():
    c = canvas.Canvas("AssertionForge/data/apb/spec/apb_spec.pdf", pagesize=A4)
    width, height = A4
    margin = 0.5 * inch
    text_width = width - 2 * margin
    
    text_object = c.beginText()
    text_object.setTextOrigin(margin, height - margin)
    text_object.setFont("Helvetica", 11)
    
    content = """The APB (Advanced Peripheral Bus) is part of the AMBA protocol family. It provides a low-cost interface that is optimized for minimal power consumption and reduced interface complexity.

The APB interface consists of the following signals:
- PCLK: Clock signal.
- PRESETn: Active low reset signal.
- PADDR: Address bus (up to 32 bits).
- PSEL: Select signal.
- PENABLE: Enable signal.
- PWRITE: Read/Write control signal. High for write, low for read.
- PWDATA: Write data bus (up to 32 bits).
- PRDATA: Read data bus (up to 32 bits).
- PREADY: Ready signal.
- PSLVERR: Slave error signal.

Protocol Operation:
The state machine for APB transfers includes IDLE, SETUP, and ACCESS states.

1. IDLE: Default state. PSEL and PENABLE are low.

2. SETUP: When a transfer is required, the bus moves to SETUP.
   - PSEL is asserted.
   - PENABLE remains low.
   - Address, Write, and Data signals must be stable.

3. ACCESS: The bus moves to ACCESS on the next clock edge.
   - PENABLE is asserted.
   - PSEL remains high.
   - If PREADY is high, the transfer completes at the end of the ACCESS cycle, and the bus returns to IDLE (or SETUP if another transfer follows).
   - If PREADY is low, the bus remains in ACCESS state until PREADY goes high.

Write transfers:
Address, write data (PWDATA), PWRITE, and PSEL are asserted at the start of the transfer. PENABLE is asserted one cycle later.

Read transfers:
Address, PWRITE, and PSEL are asserted at the start. PENABLE is asserted one cycle later. The slave must provide data on PRDATA when PENABLE is high and PREADY is high.

Error response:
PSLVERR indicates an error condition on the transfer. It is valid only when PSEL, PENABLE, and PREADY are all high.
"""
    
    lines = content.split('\n')
    y_pos = height - margin
    line_height = 14
    
    for line in lines:
        if y_pos < margin:
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText()
            text_object.setTextOrigin(margin, height - margin)
            text_object.setFont("Helvetica", 11)
            y_pos = height - margin

        text_object.textLine(line)
        y_pos -= line_height

    c.drawText(text_object)
    c.save()

if __name__ == "__main__":
    create_apb_spec()
