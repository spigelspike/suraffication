import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
import time

def show_preview(frame_generator, delay_ms=33):
    """
    Shows a live preview of the generated frames using Tkinter.
    frame_generator: iterator yielding numpy arrays (RGB)
    delay_ms: delay between frames in milliseconds
    """
    print("Opening preview window...")
    root = tk.Tk()
    root.title("py-surrafication Live Preview")
    
    # Label to hold the image
    label = tk.Label(root)
    label.pack()
    
    # Generator wrapper to keep state
    gen = iter(frame_generator)
    
    def update_frame():
        try:
            # Get next frame
            frame = next(gen)
            
            # Convert to PIL Image
            img = Image.fromarray(frame)
            
            # Convert to ImageTk
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update label
            label.imgtk = imgtk # Keep reference
            label.configure(image=imgtk)
            
            # Schedule next update
            root.after(delay_ms, update_frame)
            
        except StopIteration:
            print("Animation finished.")
            # Optionally close or keep open?
            # Let's keep open for a moment or just close?
            # Usually better to keep open so user can see final result.
            # But for a tool, maybe just close.
            # Let's wait 2 seconds then close.
            root.after(2000, root.destroy)
        except Exception as e:
            print(f"Error in preview: {e}")
            root.destroy()

    # Start loop
    root.after(0, update_frame)
    root.mainloop()
