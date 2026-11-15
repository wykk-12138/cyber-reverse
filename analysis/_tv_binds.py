import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
tv = sorted(d.get('Cybersole.Ui.Views.Tasks.TaskView', []))
print(len(tv))
print(', '.join(tv))
