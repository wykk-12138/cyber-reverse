import io
p = r'src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
new_p = r'src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs.new'
src = io.open(p, encoding='utf-8').read()
new = io.open(new_p, encoding='utf-8').read()
# the new file: drop its usings + namespace, keep from the doc comment of the class
start_new = new.index('/// <summary>')
class_new = new[start_new:]
# in the original: replace from the class doc comment that precedes AnalyticsView to its closing brace
start_old = src.index('/// <summary>\n/// Analytics page')
end_marker = '\n/// <summary>\n/// Checkout feed'
end_old = src.index(end_marker)
out = src[:start_old] + class_new.rstrip() + '\n' + src[end_old:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('replaced', end_old - start_old, 'chars with', len(class_new))
