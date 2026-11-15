import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\IDBEvidenceTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>The unrecoverable list is present"
add = '''    /// <summary>
    /// R92 added the store-name method section: how the image stores a store name (a type name plus
    /// a 0x1b 0x08 suffix, which defeats a dollar-anchored regex) and that the same stores appear in
    /// User-Agent literals — which is how OffSpring turned out to be a Poq app rather than Magento.
    /// </summary>
    [Fact]
    public void TheStoreNameMethodIsRecorded()
    {
        var doc = Doc();

        Assert.Contains("## 店铺名的存放方式", doc);
        Assert.Contains("poq.ios", doc);
        Assert.Contains("不足以枚举全部店铺", doc);

        _out.WriteLine("store-name method recorded");
    }

'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "TheStoreNameMethodIsRecorded" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("test added")
