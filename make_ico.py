from PIL import Image

# Let's crop the cat head from cat_gray.png (row 0, col 0 is sitting cat)
im = Image.open(r"C:\Users\Ubeydullah\.gemini\antigravity\scratch\taskbar_todo\assets\cat_gray.png")
# Cat sits in 32x32 cell (0, 0, 32, 32)
cat_cell = im.crop((0, 0, 32, 32))

# Save as .ico
cat_cell.save(r"C:\Users\Ubeydullah\.gemini\antigravity\scratch\taskbar_todo\assets\cat_tray.ico", format="ICO", sizes=[(16, 16), (32, 32)])
print("Successfully saved cat_tray.ico!")
