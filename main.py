import json
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
from kivy.clock import Clock

DATA_FILE = "products_data.json"

KV = '''
BoxLayout:
    orientation: 'vertical'
    spacing: dp(10)
    padding: dp(20)

    MDTopAppBar:
        title: "Gestion des Achats"
        md_bg_color: app.theme_cls.primary_color
        specific_text_color: 1, 1, 1, 1


    MDLabel:
        id: balance_label
        text: f"Montant restant : {app.remaining_balance} DH"
        halign: 'center'
        font_style: 'H5'
        theme_text_color: 'Primary'

    MDTextField:
        id: product_name
        hint_text: "Nom du produit"
        mode: "rectangle"

    MDTextField:
        id: product_price
        hint_text: "Prix du produit"
        mode: "rectangle"
        input_filter: 'int'

    MDRaisedButton:
        text: "Ajouter"
        pos_hint: {"center_x": 0.5}
        md_bg_color: app.theme_cls.primary_color
        on_release: app.add_product()

    MDLabel:
        text: "Liste des produits :"
        font_style: 'Subtitle1'
        theme_text_color: 'Secondary'

    ScrollView:
        MDList:
            id: product_list
'''

class ProductListItem(OneLineAvatarIconListItem):
    """عنصر مخصص للقائمة يحتوي على زر الحذف."""
    def __init__(self, product_name, product_price, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.text = f"{product_name} - {product_price} DH"
        self._delete_callback = delete_callback

        # إضافة زر الحذف
        delete_button = IconRightWidget(icon="trash-can", on_release=self.delete_item)
        self.add_widget(delete_button)

    def delete_item(self, instance):
        # استدعاء وظيفة الحذف من التطبيق
        self._delete_callback(self)

class ProductApp(MDApp):
    remaining_balance = NumericProperty(2000)

    def build(self):
        # تحميل واجهة المستخدم
        root = Builder.load_string(KV)
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # تأجيل استدعاء load_data إلى أن تصبح الواجهة جاهزة
        Clock.schedule_once(self.load_data, 0)

        return root

    def add_product(self):
        # الحصول على بيانات المنتج
        product_name = self.root.ids.product_name.text
        product_price = self.root.ids.product_price.text

        # التحقق من المدخلات
        if not product_name or not product_price.isdigit():
            return

        product_price = int(product_price)

        # التحقق من المبلغ المتبقي
        if product_price > self.remaining_balance:
            self.root.ids.product_name.text = ""
            self.root.ids.product_price.text = ""
            return

        # تحديث المبلغ المتبقي
        self.remaining_balance -= product_price
        self.root.ids.balance_label.text = f"Montant restant : {self.remaining_balance} DH"

        # إضافة المنتج للقائمة
        self.add_product_to_list(product_name, product_price)

        # حفظ المنتج في البيانات
        self.save_data()

        # تفريغ الحقول
        self.root.ids.product_name.text = ""
        self.root.ids.product_price.text = ""

    def add_product_to_list(self, product_name, product_price):
        # إضافة عنصر إلى القائمة
        product_item = ProductListItem(
            product_name=product_name,
            product_price=product_price,
            delete_callback=self.remove_product_from_list
        )
        self.root.ids.product_list.add_widget(product_item)

    def remove_product_from_list(self, product_item):
        # حذف العنصر من القائمة
        self.root.ids.product_list.remove_widget(product_item)

        # تحديث المبلغ المتبقي
        product_name, product_price_text = product_item.text.split(" - ")
        product_price = int(product_price_text.split(" ")[0])
        self.remaining_balance += product_price
        self.root.ids.balance_label.text = f"Montant restant : {self.remaining_balance} DH"

        # حفظ البيانات
        self.save_data()

    def save_data(self):
        # حفظ البيانات إلى ملف JSON
        data = {
            "balance": self.remaining_balance,
            "products": [
                {
                    "name": item.text.split(" - ")[0],
                    "price": int(item.text.split(" - ")[1].split(" ")[0])
                }
                for item in self.root.ids.product_list.children
            ]
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self, *args):
        # قراءة البيانات من الملف
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            self.remaining_balance = data["balance"]
            self.root.ids.balance_label.text = f"Montant restant : {self.remaining_balance} DH"
            for product in data["products"]:
                self.add_product_to_list(product["name"], product["price"])
        except FileNotFoundError:
            self.remaining_balance = 2000

if __name__ == "__main__":
    ProductApp().run()
