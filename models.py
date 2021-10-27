import os
import enum
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Enum, Boolean, Table, ForeignKeyConstraint, asc, desc
from sqlalchemy import create_engine, engine_from_config, desc
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from transitions import Machine
from sqlalchemy.ext.declarative import declared_attr

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:wsuser123@localhost:3310/wsdata123'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:wsuser123@/wsdata123?unix_socket=/cloudsql/weavesmart-central-247206:asia-south1:wsdata'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:wsuser123@/wsdata123?unix_socket=/cloudsql/weavesmart-central-247206:asia-south1:wsdata'

# SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
# print('SQLALCHEMY_DATABASE_URI', SQLALCHEMY_DATABASE_URI)

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_size=50, max_overflow=100, pool_pre_ping=True, pool_recycle=200)
Base = declarative_base()
session = scoped_session(sessionmaker(bind=engine))
print('session', session)
Base._session = session

print('after base session ')
class StateMixin(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def status(cls):
        return Column(String(45))

    @property
    def state(self):
        return self.status

    @state.setter
    def state(self, value):
        if self.status != value:
            self.status = value

    def after_state_change(self):
        self._session.add(self)
        self._session.commit()

    @classmethod
    def init_state_machine(cls, obj, *args, **kwargs):
        # when we load data from the DB(via query) we need to set the proper initial state
        initial = obj.status or 'created'

        machine = Machine(model=obj, states=states, transitions=transitions, initial=initial,
                          after_state_change='after_state_change')

        # in case that we need to have machine obj in model obj
        setattr(obj, 'machine', machine)


# Product
class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer(), primary_key=True)
    title = Column(String(200))
    cluster = Column(String(20))
    prodtype = Column(String(10))
    fabric = Column(String(30))
    upload_datetime = Column(DateTime(timezone=True), default=datetime.now)
    batch_tag = Column(String(100))
    description = Column(String(10000))
    batch_id = Column(String(12))
    weight = Column(String(45))
    skus = relationship('SKU', backref='product')
    imgs = relationship('ProductImage', backref='product')

    def __repr__(self):
        return "<Product(id='%s', cluster=%s, prodtype=%s, title=%s,fabric=%s,description=%s)>" % (
        self.id, self.cluster, self.prodtype, self.title, self.fabric, self.description)


# Product Image
class ProductImage(Base):
    __tablename__ = 'product_image'
    id = Column(Integer(), primary_key=True)
    hash_value = Column(String(100))
    img_path = Column(String(1000))
    product_id = Column(Integer(), ForeignKey('product.id', ondelete='CASCADE'))

    def __repr__(self):
        return "<ProductImage(id='%s', prod_id=%s,hash_value=%s,img_path=%s)>" % (
        self.id, self.product_id, self.hash_value, self.img_path)


# Defining Seller types enum
class SellerType(enum.Enum):
    DS = "Direct Seller"
    RS = "Reseller"
    SW = "Swahasta"
    OS = "Office Stock"
    CL = 'Clusters'


class SellerStatus(enum.Enum):
    CBNOY = "Contacted_but_not_onboarded_Yet"
    YTC = "Yet to call"
    NS = "Not suitable"
    TRNI = "They are not interested"
    OB = "Onboarded"
    CM = "Cancelled_membership"
    PNC = "phone not connected"
    PNL = "phone not lifting"


# Seller
class Seller(Base):
    __tablename__ = 'seller'
    id = Column(String(25), primary_key=True)
    name = Column(String(50))
    phone = Column(String(15))
    alternate_number = Column(String(15))
    email = Column(String(100))
    type = Column(Enum(SellerType))
    create_date = Column(DateTime(timezone=True), default=datetime.now)
    cluster = Column(String(50))
    city = Column(String(30))
    fb_page = Column(String(500))
    state = Column(Enum(SellerStatus))
    score = Column(Integer())
    no_of_prods = Column(Integer())
    skus = relationship('SKU', backref='seller')

    def __repr__(self):
        return "<Seller(id='%s', name=%s, phone=%s )>" % (self.id, self.name, self.phone)


# SKU
class sendtoResellers(Base):
    __tablename__ = 'send_to_sellers'
    sno = Column(Integer(), primary_key=True)
    product_id = Column(String(25))
    from_seller = Column(String(100))
    to_seller = Column(String(100))
    sent_date = Column(String(70))
    batch_id = Column(String(15))
    weavesmart_purchase_price = Column(String(45))
    weavesmart_selling_price = Column(String(45))

    def __repr__(self):
        return "<sendtoResellers(batch_id %s)>" % (self.batch_id)


# Defining Customer types enum
class CustomerType(enum.Enum):
    IN = "Individual"
    RS = "Reseller"
    WS = "Wholesale"
    MS = 'MailSent'
    SM = 'SendMail'


class EmailMarketing(Base):
    __tablename__ = 'email_marketing'
    id = Column(String(25), primary_key=True)
    customer_name = Column(String(50))
    customer_id = Column(String(30))
    mail_status = Column(String(20))
    mails_sent_date = Column(DateTime(timezone=True), default=datetime.now)

    def __repr__(self):
        return "<EmailMarketing(customer_id='%s', customer_name=%s, mail_status=%s )>" % (
        self.customer_id, self.customer_name, self.mail_status)


class ShopCustomer(Base):
    __tablename__ = 'shop_customers'
    id = Column(Integer(), primary_key=True)
    full_name = Column(String(150))
    customer_id = Column(String(100))

    # email = Column(String(100))

    def __repr__(self):
        return "ShopCustomer (full_name = %s, customer_id=%s)>" % (self.full_name, self.customer_id)


# Customer
class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer(), primary_key=True)
    first_name = Column(String(150))
    last_name = Column(String(250))
    reg_mobile_number = Column(String(15))
    alternate_number = Column(String(15))
    email = Column(String(45))
    email_verified = Column(Boolean())
    whatsapp_number = Column(String(15))
    customer_type = Column(Enum(CustomerType))
    customer_id = Column(String(100))
    accepts_marketing = Column(Boolean())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_visited = Column(DateTime(timezone=True), onupdate=func.now())

    # whatsapp_group = Column(String(100))
    orders = relationship('Orders', backref='customer')
    addresses = relationship('CustomerAddress', backref='customer')

    def __repr__(self):
        return "Customer (Name = %s %s)>" % (self.first_name, self.last_name)


# addresses_of_customers
class CustomerAddress(Base):
    __tablename__ = 'customer_address'
    id = Column(Integer(), primary_key=True)
    shopify_address_id = Column(String(50))
    name = Column(String(250))

    address = Column(String(500))

    city = Column(String(250))
    state = Column(String(45))
    country = Column(String(45))
    pincode = Column(String(10))
    mobile = Column(String(15))
    default = Column(Boolean())
    # cust_id = Column(String(50))
    cust_id = Column(Integer(), ForeignKey('customer.id', ondelete='CASCADE'))
    def __repr__(self):
        return "Address (id = %s, customer-%s , shopifyid = %s)>" % (self.id, self.cust_id, self.shopify_address_id)


# Defining payment mode enum
class PaymentModeEnum(enum.Enum):
    cod = "Cash On Delivery"
    paid = "Paid Order"
    cbs = "Collect Before Shipment"


# Association table for Orders - CustomerShipment
# order_cshipment = Table('order_cshipment', Base.metadata,
#                         Column('order_id', Integer(), ForeignKey("orders.order_id")),
#                         Column('cship_id', String(45), ForeignKey("customer_shipment.id"))
#                         )

# # Customer Shipment
# class ShimentFsmLog(Base):
#     __tablename__ = 'shipment_fsm_log'
#     order_id = Column(Integer(), ForeignKey('orders.order_id', ondelete='CASCADE'), primary_key=True)
#     sku_id = Column(String(45), ForeignKey('sku.id', ondelete='CASCADE'), primary_key=True)
#     cship_id = Column(String(50), ForeignKey('customer_shipment.id', ondelete='CASCADE'), primary_key=True)
#     in_fsm_state = Column(String(500), primary_key=True)
#     out_fsm_state = Column(String(500))
#     state_in_time = Column(DateTime(timezone=True), default=datetime.now, primary_key=True)
#     state_out_time = Column(DateTime(timezone=True))
#
#     # ordersku = relationship("OrderSKU", foreign_keys=[order_id, sku_id], backref='orderskufsmlog')
#     # __table_args__ = (ForeignKeyConstraint(("order_id", "sku_id", "service_id"), (OrderSKU.order_id, OrderSKU.sku_id, OrderSKU.service_id)))
#
#     def __repr__(self):
#         return "<OrderSKUFsmLog(order_id='%s', sku_id='%s', service_id='%s', fsm_state=%s,out_fsm_state=%s)>" % (self.order_id, self.sku_id, self.service_id, self.fsm_state,self.out_fsm_state)
class CustomerShipment(Base):
    __tablename__ = 'customer_shipment'
    id = Column(Integer(), primary_key=True)
    courier_name = Column(String(15))
    tracking_number = Column(String(45))
    from_city = Column(String(15))
    ship_date = Column(Date())
    to_city = Column(String(15))
    delivered_date = Column(Date())
    eta = Column(Date())
    status = Column(String(15))
    # orders = relationship('Orders', secondary=ShimentFsmLog, backref='c_shipments')

    def __repr__(self):
        return "<CustomerShipment(id='%d', status=%s)>" % (self.order_id, self.status)

# Defining Customer types enum
class OrderPriority(enum.Enum):
    HIGH = "High Priority"
    MEDIUM = "Medium Priority"
    LOW = "Low Priority"

# Order
class Orders(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer(), primary_key=True)
    state = Column(String(45))
    received_date = Column(DateTime(timezone=True), server_default=func.now())
    sales_channel = Column(String(45))
    cust_id = Column(Integer(), ForeignKey('customer.id', ondelete='CASCADE'))

    order_value = Column(Integer())
    payment_mode = Column(Enum(PaymentModeEnum))
    last_update_date = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(String(5000))
    no_of_skus = Column(Integer())

    total_weight = Column(Integer())
    shipping_address_id = Column(String(50))
    billing_address_id = Column(String(50))
    shipping_charge = Column(Integer())

    tax_amount = Column(Integer())
    confirmation = Column(Boolean())
    ship_by_date = Column(Date())
    priority = Column(Enum(OrderPriority))
    part_ship_ok = Column(Boolean())
    discount = Column(String(50)) # discount code
    discount_type = Column(String(50)) #write wallet and direct names
    discount_amt = Column(Integer())# discout amount
    Status = Column(String(45))
    checkout_id = Column(String(50))
    orderskus = relationship('OrderSKU', backref='order')
    # cshipments = relationship('CustomerShipment', secondary=ShimentFsmLog, backref='order')
    cpayments = relationship('CustomerPayment', backref='order')

    def __repr__(self):
        return "<Order(id='%d', state=%s)>" % (self.order_id, self.state)


# Order_SKU
class OrderSKU(Base):
    __tablename__ = 'order_sku'
    order_id = Column(Integer(), ForeignKey('orders.order_id', ondelete='CASCADE'), primary_key=True)
    sku_id = Column(String(45), ForeignKey('sku.id', ondelete='CASCADE'), primary_key=True)
    service_id = Column(String(100), primary_key=True)
    alted_sku_id = Column(String(45))
    lineitem_qty = Column(Integer())
    lineitem_price = Column(Integer())
    pending_on_user = Column(String(10))
    seller_pay_status = Column(String(10))
    ship_id = Column(String(45), ForeignKey('seller_shipment.id', ondelete='CASCADE'))
    seller_payment_id = Column(Integer(), ForeignKey('seller_payment.id', ondelete='CASCADE'))
    status = Column(String(45))
    status_detailed = Column(String(100))
    pending_on_role_id = Column(String(100))
    properties = Column(String(8000))
    # orderskufsmlog = relationship('OrderSKUFsmLog', backref='ordersku')
    def __repr__(self):
        return "<OrderSKU(order_id='%d', sku_id=%s)>" % (self.order_id, self.sku_id)

class NRanges(Base):
    __tablename__ = 'nranges'
    id = Column(Integer(), primary_key=True)
    username = Column(String(100), primary_key=True)
    user_id = Column(String(100))
    department = Column(String(100), primary_key=True)
    role_id = Column(String(100))
    entry_fsm_state = Column(String(200), primary_key=True)
    out_fsm_state = Column(String(200), primary_key=True)
    status = Column(String(100))
    def __repr__(self):
        return "<NRanges(username=%s,department=%s, Entry fsm state =%s,Out fsm state =%s,status =%s)>" % (self.username, self.department,self.entry_fsm_state, self.out_fsm_state,self.status)
# Seller Shipment
class SellerShipment(Base):
    __tablename__ = 'seller_shipment'
    id = Column(String(45), primary_key=True)
    courier_name = Column(String(15))
    tracking_number = Column(String(45))
    from_city = Column(String(15))
    ship_date = Column(Date())
    to_city = Column(String(15))
    received_date = Column(Date())
    eta = Column(Date())
    status = Column(String(15))
    ordersku = relationship('OrderSKU', backref='s_shipment')

    def __repr__(self):
        return "<SellerShipment(id='%d', status=%s)>" % (self.order_id, self.status)



class OrderSKUFsmLog(Base):
    __tablename__ = 'order_sku_fsm_log'
    order_id = Column(Integer(),ForeignKey('orders.order_id', ondelete='CASCADE'), primary_key=True)
    sku_id = Column(String(45),ForeignKey('sku.id', ondelete='CASCADE'), primary_key=True)
    service_id = Column(String(50), primary_key=True)
    fsm_state = Column(String(500), primary_key=True)
    out_fsm_state = Column(String(500))
    state_in_time = Column(DateTime(timezone=True), default=datetime.now, primary_key=True)
    state_out_time = Column(DateTime(timezone=True))
    in_user = Column(String(30))
    out_user = Column(String(30))
    state_changed_by = Column(String(500))
    # ordersku = relationship("OrderSKU", foreign_keys=[order_id, sku_id], backref='orderskufsmlog')
    # __table_args__ = (ForeignKeyConstraint(("order_id", "sku_id", "service_id"), (OrderSKU.order_id, OrderSKU.sku_id, OrderSKU.service_id)))

    def __repr__(self):
        return "<OrderSKUFsmLog(order_id='%s', sku_id='%s', service_id='%s', fsm_state=%s,out_fsm_state=%s)>" % (self.order_id, self.sku_id, self.service_id, self.fsm_state,self.out_fsm_state)


class CustomerPayment(Base):
    __tablename__= 'customer_payment'
    id = Column(Integer(), primary_key=True)
    order_id = Column(Integer(), ForeignKey('orders.order_id', ondelete='CASCADE'))
    payment_channel = Column(String(10))
    transaction_id = Column(String(10))
    request_date = Column(Date())
    received_date = Column(Date())
    amount_received = Column(Integer())
    status = Column(Boolean())

    def __repr__(self):
        return "<CustomerPayment(order_id='%d', payment_status=%s)>" % (self.order_id, self.status)


class SellerPayment(Base):
    __tablename__ = 'seller_payment'
    id = Column(Integer(), primary_key=True)
    seller_name = Column(String(100))
    payment_channel = Column(String(10))
    transaction_id = Column(String(10))
    payment_date = Column(Date())
    amount_paid = Column(Integer())
    status = Column(Boolean())
    ordersku = relationship('OrderSKU', backref='seller_payment', uselist=False)

    def __repr__(self):
        return "<SellerPayment(id='%d', payment_status=%s)>" % (self.id, self.status)



class WsCodes(Base):
    __tablename__ = 'ws_codes'
    name = Column(String(45))
    code = Column(String(5), primary_key=True)
    type = Column(String(25))
    last_sku_num = Column(Integer())

    def __repr__(self):
        return "<WsCodes(name=%s,type = %s ,code=%s)>" % (self.name, self.code, self.type)


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('user.id'))
    role_id = Column(Integer(), ForeignKey('role.id'))

    def __repr__(self):
        return "<RolesUsers(user_id=%d,role_id = %d)>" % (self.user_id, self.role_id)


class UserAttendence(Base):
    __tablename__ = 'user_attendence'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer())
    last_login_at = Column(DateTime(timezone=True), server_default=func.now())
    current_login_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    confirmed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "<UserAttendence(user_id=%d,active = %s)>" % (self.user_id, self.active)


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)


    def __repr__(self):
        return "<Role(name=%s)>" % (self.name)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    email = Column(String(255), unique=True)
    mobile_number = Column(String(20))
    OTP = Column(String(10))
    username = Column(String(255))
    password = Column(String(255))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now())

    # sku = relationship('SKU', backref='user')

    def __repr__(self):
        return "<User(username=%s,mobile_number = %s, password=%s)>" % (
        self.username, self.mobile_number, self.password)


class TransactionMode(enum.Enum):
    RF = "Refund"
    CBC = "CashBackOnCart"
    CBP = "CashBackOnProduct"
    CBF = "CashBackOnFirstPurchase"
    CBM = "CashBackOnFirst"


class TransactionPlatForm(enum.Enum):
    MB = "Mobile"
    WB = "WEB"


class TransactionStatus(enum.Enum):
    CM = "Completed"
    PN = "Pending"


class Transactions(Base):
    __tablename__ = 'transaction'
    id = Column(Integer(), primary_key=True)
    order_id = Column(String(60))
    cust_id = Column(String(100))
    type = Column(String(20))
    cus_amount = Column(String(15))
    amount = Column(String(15))
    mode = Column(Enum(TransactionMode))
    platform = Column(Enum(TransactionPlatForm))
    cust_ifsc_code = Column(String(20))
    cust_acc_num = Column(String(20))
    status = Column(Enum(TransactionStatus))
    transac_id = Column(String(40))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "Transactions (id = %d, mode=%s, platform=%s, status=%s)>" % (
        self.id, self.mode, self.platform, self.status)


class Refund(Base):
    __tablename__ = 'refund'
    id = Column(Integer(), primary_key=True)
    order_id = Column(String(60))
    cust_id = Column(String(100))
    type = Column(String(20))
    cus_amount = Column(String(15))
    refunded_amount = Column(String(15))
    cust_ifsc_code = Column(String(20))
    cust_acc_num = Column(String(20))
    status = Column(String(40))
    transac_id = Column(String(40))
    refund_created_at = Column(DateTime(timezone=True), server_default=func.now())
    refund_done_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "Refund (id = %d, order_id-%s)>" % (self.id, self.order_id)


class RefundAssociation(Base):
    __tablename__ = 'refund_association'
    id = Column(Integer(), primary_key=True)
    refund_id = Column(Integer())
    sku_id = Column(String(30))
    ord_id = Column(String(100))

    def __repr__(self):
        return "RefundAssociation (refund_id = %d, sku_id=%s, ord_id=%s)>" % (self.refund_id, self.sku_id, self.ord_id)


class Wallet(Base):
    __tablename__ = 'wallet'
    id = Column(Integer(), primary_key=True)
    cust_id = Column(String(100))
    amount = Column(String(30))
    amt_add_in_wallet_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "Wallet (cust_id = %s, amount-%s)>" % (self.cust_id, self.amount)


'''
class products_reports(Base):
    __tablename__ = 'product_reports'
    reportTime = Column(DateTime(timezone=True), server_default=func.now(), primary_key=True)
    totalProducts = Column(Integer())
    uploadProducts = Column(Integer())
    dontUploadProducts = Column(Integer())
    matchedProducts = Column(Integer())
    pendingProducts = Column(Integer())

    def __repr__(self):
        return "<products_reports(totalProducts=%d)>" % (self.totalProducts)


class imported_type(enum.Enum):
    IC = "ImportCompleted"
    NI = "notImported"



class csvfiles(Base):
    __tablename__ = 'imported_csvs'
    sno = Column(Integer(), primary_key=True)
    file_name = Column(String(100))
    file_path = Column(String(200))
    create_datetime = Column(DateTime(timezone=True), server_default=func.now())
    downloaded_datetime = Column(DateTime(timezone=True), server_default=func.now())
    completed_csv = Column(Enum(imported_type))

    def __repr__(self):
        return "<csvfiles(sno=%d, file_name=%s,create_datetime=%s, file_path=%s, completed_csv=%s)>" % (self.sno,self.file_name,self.create_datetime ,self.file_path,self.completed_csv)


class Tags(Base):
    __tablename__ = 'tags'
    name = Column(String(50), primary_key=True)
    description = Column(String(500))
    create_date = Column(DateTime(timezone=True), server_default=func.now())
    sku_tags = relationship('SKU', secondary='AssociationBetweenSkuTag', backref='tags')


    def __repr__(self):
        return "<Tags(name='%s')>" % (self.name)

class AssociationBetweenSkuTag(Base):
    __tablename__ = 'associationskutag'
    id = Column(Integer(), primary_key=True)
    sku_id = Column(String(45), ForeignKey('sku.id', ondelete='CASCADE'))
    tag_name = Column(String(50), ForeignKey('tags.name', ondelete='CASCADE'))

    def __repr__(self):
        return "<AssociationBetweenSkuTag(sku_id='%s', tag_name=%s)>" % (self.sku_id, self.tag_name)
'''


# Defining Seller types enum
class skuShopifyStatus(enum.Enum):
    UPB = "Un_published"
    PB = "Published"
    UP = "Upload"
    OD = 'order product'
    DPB = "Delay_published"
    DU = "Dont_upload"
    IM = "Imported"
    DTD = "Deleted"
    DPC = "DuplicateProduct"
    CSV = 'productsImportedNotPublished'
    DPUPB = 'duplicateUnpublished'
    DPDU = 'duplicateDontUpload'
    CLUP = 'ClusterProducts'


class SKU(Base):
    __tablename__ = 'sku'
    id = Column(String(45), primary_key=True)
    seller_code = Column(String(50))
    seller_id = Column(String(10), ForeignKey('seller.id', ondelete='CASCADE'))
    p_price = Column(Integer())
    s_price = Column(Integer())
    shipping_charges = Column(Integer())
    gst = Column(String(30))
    create_datetime = Column(DateTime(timezone=True), server_default=func.now())
    product_id = Column(Integer(), ForeignKey('product.id', ondelete='CASCADE'))
    # publish_status = Column(String(10))
    publish_status = Column(Enum(skuShopifyStatus))
    inventory_qty = Column(Integer(), default=1)
    Tags = Column(String(100))
    user_id = Column(String(20))
    notes = Column(String(1000))
    inventory_days = Column(String(20))
    uploaded_datetime = Column(DateTime(timezone=True), server_default=func.now())
    unpublished_datetime = Column(DateTime(timezone=True), server_default=func.now())

    # shopify_prod_id = Column(String(20))
    # orderskus = relationship('OrderSKU', backref='sku')
    # tagged_skus = relationship('AssociationBetweenSkuTag', backref='tag')

    def __repr__(self):
        return "<SKU(id='%s', p_price=%s,seller_id=%s,publish_status=%s, create_datetime=%s, user_id=%s)>" % (
        self.id, self.p_price, self.seller_id, self.publish_status, self.create_datetime, self.user_id)


class WhatsappBatch(Base):
    __tablename__ = 'whatsapp_batch'
    batch_id = Column(Integer(), primary_key=True)
    seller_id = Column(String(10))
    notes = Column(String(500))
    images = relationship('WhatsappImage', backref='whatsapp_batch')

    def __repr__(self):
        return "<WhatsappGroups(batch_id='%d', notes=%s)>" % (self.batch_id, self.notes)


# class Whatsapp_association(Base):
#     __tablename__ = 'whatsapp_association'
#     seller_id = Column(String(10), primary_key=True)
#     date = Column(DateTime(timezone=True), server_default=func.now())
#     whatsapp_Count = Column(Integer())
#     upload_input_count = Column(Integer())
#     upload_output_count = Column(Integer())
#

class Drive(Base):
    __tablename__ = 'drive'
    id = Column(Integer(), primary_key=True)
    folder_id = Column(String(200))


class WhatsappImage(Base):
    __tablename__ = 'whatsapp_image'
    image_id = Column(Integer(), primary_key=True)
    image_path = Column(String(200))
    batch_id = Column(Integer(), ForeignKey('whatsapp_batch.batch_id', ondelete='CASCADE'))

    def __repr__(self):
        return "<WhatsappImages(image_id='%d', image_path=%s)>" % (self.image_id, self.image_path)


class BackendServices(Base):
    __tablename__ = 'backendservices'
    id = Column(Integer(), primary_key=True)
    servicename = Column(String(300))
    status = Column(String(10))
    SellerId = Column(String(10))
    allstatus = Column(String(20))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    productstatus = Column(String(20))
    inventoryDate = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "<BackendServices(servicename='%s', status=%s)>" % (self.servicename, self.status)


class Tag(Base):
    __tablename__ = 'tags'
    tag_name = Column(String(255), primary_key=True)
    tag_description = Column(String(255))
    create_date = Column(DateTime(timezone=True), server_default=func.now())


class Product_Tag_Association(Base):
    __tablename__ = 'product_tag_association'
    id = Column(Integer(), primary_key=True)
    product_id = Column(Integer(), ForeignKey('product.id', ondelete='CASCADE'))
    tag = Column(String(255), ForeignKey('tags.tag_name', ondelete='CASCADE'))


class skuAmazonStatus(enum.Enum):
    UPB = "Un_published"
    PB = "Published"
    AO = 'Amazon_order'
    DTD = 'Deleted'


class Amazon_Sku(Base):
    __tablename__ = 'amazon_sku'
    a_sku = Column(String(30), primary_key=True)
    created_date = Column(DateTime(timezone=True), default=datetime.now())
    status = Column(Enum(skuAmazonStatus))


class Amazon_mapping_sku(Base):
    __tablename__ = 'amazon_mapping'
    shopify_sku = Column(String(30), primary_key=True)
    created_date = Column(DateTime(timezone=True), default=datetime.now())
    amazon_sale_price = Column(Integer())
    amazon_sku_id = Column(String(15), ForeignKey('amazon_sku.a_sku', ondelete='CASCADE'))


class Amazon_Order(Base):
    __tablename__ = 'amazon_orders'
    id = Column(Integer(), primary_key=True)
    order_id = Column(Integer())
    amazon_sku = Column(String(50))
    shopify_sku = Column(String(50))
    created_date = Column(DateTime(timezone=True))
    lineitem_qty = Column(Integer())
    title = Column(String(500))
    lineitem_price = Column(Integer())


# for mobile app
class Category(Base):
    __tablename__ = 'categories'
    category_id = Column(Integer(), primary_key=True)
    category_name = Column(String(200))
    cat_image_link = Column(String(1000))
    description = Column(String(1000))

    def __repr__(self):
        return "<Category(cotegory_id='%d', category_name=%s)>" % (self.cotegory_id, self.category_name)


class SubCategory(Base):
    __tablename__ = 'sub_categories'
    sub_cat_id = Column(Integer(), primary_key=True)
    sub_cat_name = Column(String(200))
    description = Column(String(1000))
    sub_cat_img_link = Column(String(1000))

    def __repr__(self):
        return "<SubCategory(sub_cat_id='%d', sub_cat_name=%s)>" % (self.sub_cat_id, self.sub_cat_name)


class Collection(Base):
    __tablename__ = 'collections'
    collection_id = Column(Integer(), primary_key=True)
    collection_name = Column(String(200))
    description = Column(String(1000))
    image_path = Column(String(1000))

    def __repr__(self):
        return "<Collection(collection_id='%d', sub_cat_name=%s)>" % (self.collection_id, self.collection_name)


class SubCollection(Base):
    __tablename__ = 'sub_collections'
    sub_collect_id = Column(Integer(), primary_key=True)
    sub_collect_name = Column(String(200))
    description = Column(String(1000))
    image_path = Column(String(1000))

    def __repr__(self):
        return "<SubCollection(collection_id='%d', sub_cat_name=%s)>" % (self.collection_id, self.collection_name)


class Reseller(Base):
    __tablename__ = 'resellers'
    reseller_id = Column(Integer(), primary_key=True)
    reseller_name = Column(String(200))
    contact_number = Column(String(20))

    def __repr__(self):
        return "<Reseller(reseller_id='%d', reseller_name=%s)>" % (self.reseller_id, self.reseller_name)


class RCustomer(Base):
    __tablename__ = 'res_customers'
    customer_id = Column(Integer(), primary_key=True)
    customer_name = Column(String(200))
    contact_number = Column(Integer())

    def __repr__(self):
        return "<Customer(customer_id='%d', customer_name=%s)>" % (self.customer_id, self.customer_name)


class ResCustAsso(Base):
    __tablename__ = 'reseller_cust_associ'
    id = Column(Integer(), primary_key=True)
    reseller_id = Column(Integer(), ForeignKey('resellers.reseller_id', ondelete='CASCADE'))
    customer_id = Column(Integer(), ForeignKey('res_customers.customer_id', ondelete='CASCADE'))

    def __repr__(self):
        return "<ResCustAsso(reseller_id='%d', customer_id=%s)>" % (self.reseller_id, self.customer_id)


class ResProdAsso(Base):
    __tablename__ = 'reseller_prod_associ'
    id = Column(Integer(), primary_key=True)
    reseller_id = Column(Integer(), ForeignKey('resellers.reseller_id', ondelete='CASCADE'))
    product_id = Column(Integer(), ForeignKey('product.id', ondelete='CASCADE'))

    def __repr__(self):
        return "<ResProdAsso(reseller_id='%d', product_id=%s)>" % (self.reseller_id, self.product_id)


class ResCatAsso(Base):
    __tablename__ = 'reseller_catogery_associ'
    id = Column(Integer(), primary_key=True)
    reseller_id = Column(Integer(), ForeignKey('resellers.reseller_id', ondelete='CASCADE'))
    catogery_id = Column(Integer(), ForeignKey('categories.category_id', ondelete='CASCADE'))

    def __repr__(self):
        return "<ResCatAsso(reseller_id='%d', catogery_id=%s)>" % (self.reseller_id, self.catogery_id)


class ResSubCatAsso(Base):
    __tablename__ = 'reseller_sub_catogery_associ'
    id = Column(Integer(), primary_key=True)
    reseller_id = Column(Integer(), ForeignKey('resellers.reseller_id', ondelete='CASCADE'))
    sub_catogery_id = Column(Integer(), ForeignKey('sub_categories.sub_cat_id', ondelete='CASCADE'))

    def __repr__(self):
        return "<ResSubCatAsso(reseller_id='%d', sub_catogery_id=%s)>" % (self.reseller_id, self.sub_catogery_id)
class UserJWT(Base):
    __tablename__ = 'userJWT'
    id = Column(Integer(), primary_key = True)
    public_id = Column(String(50), unique = True)
    name = Column(String(100))
    email = Column(String(70), unique = True)
    password = Column(String(800))

    def __repr__(self):
        return "<UserJwt(id='%d', public_id=%s, name=%s ,email=%s, pass=%s)>" % (self.id, self.public_id,self.name,self.email,self.password)
states = ['created', 'validated', 'active', 'inactive']

transitions = [
    ['validated', 'created', 'validated'],
    ['enable', ['validated', 'created'], 'active'],
    ['disable', 'active', 'inactive'],
]
#
# Base.metadata.create_all(engine)
# print('success')
