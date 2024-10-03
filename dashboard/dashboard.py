import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import urllib
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })

    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_products_df(df):
    sum_order_products_df = df.groupby(by="product_category_name_english").order_id.count().sort_values(ascending=False).reset_index()
    sum_order_products_df.rename(columns={
        'product_category_name_english': 'product name',
        'order_id': 'quantity'
    }, inplace=True)
    return sum_order_products_df

def create_product_revenue_df(df):
    product_revenue_df = df.groupby(by='product_category_name_english').payment_value.sum().sort_values(ascending=False).reset_index()
    product_revenue_df.rename(columns={
        'product_category_name_english': 'product name',
        'payment_value': 'revenue'
    }, inplace=True)
    return product_revenue_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer count"
    }, inplace=True)
    return bycity_df


all_df = pd.read_csv("dashboard/main_data.csv")
geolocation_df = pd.read_csv('dashboard/Geolocation.csv')

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_products_df = create_sum_order_products_df(main_df)
product_revenue_df = create_product_revenue_df(main_df)
bycity_df = create_bycity_df(main_df)

st.title('Sales Report E-Commerce :cloud:')

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

plt.figure(figsize=(10, 5)) 
plt.plot(daily_orders_df["order_purchase_timestamp"], daily_orders_df["order_count"], marker='o', linewidth=2, color="#72BCD4") 
# plt.title("Number of Orders per Month", loc="center", fontsize=20) 
plt.xticks(fontsize=10, rotation=30)
plt.yticks(fontsize=10)
plt.ylim(bottom=0)

st.pyplot(plt)

st.write("")
st.write("")


st.subheader("Best & Worst Performing Product by Total Orders")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 15))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="quantity", y="product name", data=sum_order_products_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=30)
ax[0].tick_params(axis ='y', labelsize=25)
ax[0].tick_params(axis ='x', labelsize=25)

sns.barplot(x="quantity", y="product name", data=sum_order_products_df.sort_values(by="quantity", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=25)

st.pyplot(plt)

st.write("")
st.write("")

st.subheader("Best & Worst Performing Product by Total Revenue")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 15))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="revenue", y="product name", data=product_revenue_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Product with the Best Revenue ($Millions)", loc="center", fontsize=30)
ax[0].tick_params(axis ='y', labelsize=25)
ax[0].tick_params(axis ='x', labelsize=25)

sns.barplot(x="revenue", y="product name", data=product_revenue_df.sort_values(by="revenue", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Product with the Worse Revenue ($)", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=25)

st.pyplot(plt)

st.write("")
st.write("")

st.subheader("Customer Demographics")

plt.figure(figsize=(10, 5))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer count", 
    y="customer_city",
    data=bycity_df.sort_values(by="customer count", ascending=False).head(8),
    palette=colors_
)
plt.title("Number of Customer by City", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)
plt.show()

st.pyplot(plt)

st.write("")
st.write("")

st.subheader("Geospatial Analysis")

geolocation = geolocation_df.groupby(['geolocation_zip_code_prefix'])['geolocation_state'].nunique().reset_index(name='count')
geolocation[geolocation['count']>= 2].shape
max_state = geolocation_df.groupby(['geolocation_zip_code_prefix','geolocation_state']).size().reset_index(name='count').drop_duplicates(subset = 'geolocation_zip_code_prefix').drop('count',axis=1)
geolocation_pointer = geolocation_df.groupby(['geolocation_zip_code_prefix','geolocation_city','geolocation_state'])[['geolocation_lat','geolocation_lng']].median().reset_index()
geolocation_pointer = geolocation_pointer.merge(max_state,on=['geolocation_zip_code_prefix','geolocation_state'],how='inner')
customers_geolocation = pd.merge(
    left=main_df,
    right=geolocation_pointer,
    how='inner',
    left_on='customer_zip_code_prefix',
    right_on='geolocation_zip_code_prefix'
)
brazil_geolocation = mpimg.imread(urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
map = customers_geolocation.drop_duplicates(subset='customer_unique_id').plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10,10), alpha=0.3,s=0.3,c='red')
plt.axis('off')
plt.imshow(brazil_geolocation, extent=[-73.88283055, -33.8,-33.75116944,5.4])

st.pyplot(plt)
