import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Webhook\IWebhook.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('namespace Cybersole.Webhook;', 'namespace Cybersole.Core.Webhooks;')
t = t.replace('/// What a webhook has to be able to do (Cybersole.Webhook.IWebhook, R318).',
              '/// What a webhook has to be able to do (IWebhook, R318). The image puts it in Cybersole.Webhook; here it sits in\n/// Cybersole.Core.Webhooks because Cybersole.Webhook as a namespace collides with the Webhook class in this assembly.')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('public sealed class Webhook : Cybersole.Webhook.IWebhook', 'public sealed class Webhook : Cybersole.Core.Webhooks.IWebhook')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
# move the file to match the namespace
import os, shutil
src = p
dst = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Webhooks\IWebhook.cs"
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.move(src, dst)
os.rmdir(r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Webhook")
print('namespace moved to Cybersole.Core.Webhooks')
