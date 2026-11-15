import io

# 1) John Lewis: the /callback/login/guest?email= endpoint the census found outside the table.
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\RetailApiFamilies.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''        public const string GuestCallbackV4 = Base + "v4/callback/guest";'''
new1 = '''        public const string GuestCallbackV4 = Base + "v4/callback/guest";

        /// <summary>
        /// The guest login callback the census found outside this table in R127:
        /// <c>https://checkout.johnlewis.com/callback/login/guest?email=</c>. It sits beside the BFF
        /// rather than under it — a different first segment — which is why a scan keyed on
        /// <c>bff/</c> missed it.
        /// </summary>
        public const string GuestLoginCallback = "https://checkout.johnlewis.com/callback/login/guest?email=";'''
if old1 not in t1:
    raise SystemExit("GuestCallbackV4 anchor missing")
t1 = t1.replace(old1, new1, 1)

# add to the All list of the John Lewis family
old_all = "        GuestCallbackV4, DeliveriesV4, DeliveriesSlashV4, DeliveryAddressV4,"
if old_all in t1:
    t1 = t1.replace(old_all,
                    "        GuestCallbackV4, GuestLoginCallback, DeliveriesV4, DeliveriesSlashV4,\n"
                    "        DeliveryAddressV4,", 1)
else:
    print("warning: JL All list not found")

io.open(p1, "w", encoding="utf-8", newline="").write(t1)
print("John Lewis guest login callback added")
