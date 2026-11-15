import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()
old = '''            }));

        Relabel();
    }
}'''
if old not in t:
    old = '''            }));
        Relabel();
    }
}'''
assert old in t, 'anchor missing'
t = t.replace(old, '''            }));
    }
}''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('stray Relabel() removed from the driver modal')
