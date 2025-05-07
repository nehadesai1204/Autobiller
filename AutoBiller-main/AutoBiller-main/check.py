from billing import detected_objects



maggi_count = 0
vim_count = 0
shevat_label = 'Maggi'

final_labels = [i['label'] for i in detected_objects]

for label in final_labels:
    if label.lower() == 'maggi':
        maggi_count += 1
    elif label.lower() == 'vim':
        vim_count += 1

if maggi_count > vim_count:
    shevat_label = "Maggi"
elif vim_count > maggi_count:
    shevat_label = "Vim"

print(shevat_label)