import io
p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding='utf-8').read()
# keep the first (newest) status block only; everything below it is history and now lives in the archive file
first = t.index('最后更新：')
second = t.find('最后更新：', first + 1)
head = t[:first]
print('head length:', len(head), '| stale blocks after the first:', t.count('最后更新：') - 1)
