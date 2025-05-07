from tkinter import *
from PIL import Image, ImageTk
from check import shevat_label



# Dictionary mapping item names to their image paths
item_images = {
    "Maggi": "Maggi.jpg",
    "Vim": "Vim.jpg",
}

item_name=shevat_label

def update_image(*args):
    
    if item_name in item_images:
        img_path = item_images[item_name]
        img = Image.open(img_path)
        img = img.resize((100, 100), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img
    else:
        image_label.config(image='')

root = Tk()
root.title('Retail Billing System')
root.geometry('1270x685')

# Set the background color of the entire window
oot.config(bg='#DEF9C4')

headingLabel = Label(root, text='Retail Billing System', font=('Chilanka', 30, 'bold'),
                     bg='#468585', fg='white', bd=8, relief=GROOVE)

headingLabel.pack(fill=X, pady=10)

customer_details_frame = LabelFrame(root, text='Customer Details', font=('MathJax_Caligraphic', 15, 'bold'),
                                    bg='#50B498', fg='black', bd=8, relief=GROOVE)
customer_details_frame.pack(fill=X, pady=30)

image_label = Label(customer_details_frame, bg='#9CDBA6')
image_label.grid(row=0, column=0, padx=10, pady=4)

# Item Name
itemLabel = Label(customer_details_frame, text='Item Name:', font=('Ani', 15, 'bold'), bg='#9CDBA6', fg='teal')
itemLabel.grid(row=0, column=2, padx=10, pady=2)

itemValueLabel = Label(customer_details_frame, text='total', font=('Ani', 15, 'bold'), bg='#ffffff', fg='black')
itemValueLabel.grid(row=0, column=3, padx=5, pady=2)

# Adding extra padding to differentiate sections
Label(customer_details_frame, bg='#50B498').grid(row=0, column=4, padx=20)

# Weight
weightLabel = Label(customer_details_frame, text='Weight (grams):', font=('Ani', 15, 'bold'), bg='#9CDBA6', fg='teal')
weightLabel.grid(row=0, column=5, padx=10, pady=2)

weightValueLabel = Label(customer_details_frame, text='Weight (grams)', font=('Ani', 15, 'bold'), bg='#ffffff', fg='black')
weightValueLabel.grid(row=0, column=6, padx=5, pady=2)

# Adding extra padding to differentiate sections
Label(customer_details_frame, bg='#50B498').grid(row=0, column=7, padx=20)

# Item Count
countLabel = Label(customer_details_frame, text='Item Count:', font=('Ani', 15, 'bold'), bg='#9CDBA6', fg='teal')
countLabel.grid(row=0, column=8, padx=10, pady=2)

countValueLabel = Label(customer_details_frame, text='Item Count', font=('Ani', 15, 'bold'), bg='#ffffff', fg='black')
countValueLabel.grid(row=0, column=9, padx=5, pady=2)




update_image(item_name)

root.mainloop()
