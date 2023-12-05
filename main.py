import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

df = pd.read_csv("./data/product_data.csv", sep=";")

months_raw = "Month 1;Month 2;Month 3;Month 4;Month 5;Month 6;Month 7;Month 8;Month 9;Month 10;Month 11;Month 12;Month 13;Month 14;Month 15;Month 16;Month 17;Month 18;Month 19;Month 20;Month 21;Month 22;Month 23;Month 24;Month 25;Month 26;Month 27;Month 28;Month 29;Month 30;Month 31;Month 32;Month 34;Month 35;Month 36".split(";")

country_dic = {
    'DE': 'Germany',
    'CN': 'China',
    'GB': 'United Kingdom',
    'AU': 'Australia',
    'ES': 'Spain',
    'NL': 'Netherlands',
    'US': 'United States',
    'DK': 'Denmark',
    'BE': 'Belgium',
    'FR': 'France',
    'IT': 'Italy',
    'PL': 'Poland',
    'SE': 'Sweden',
    'TW': 'Taiwan',
    'JP': 'Japan',
    'HK': 'Hong Kong',
    'KR': 'South Korea',
    'PH': 'Philippines',
    'MY': 'Malaysia',
    'SG': 'Singapore',
    'TH': 'Thailand',
    'Id': 'Indonesia',
    'FJ': 'Fiji',
    'VN': 'Vietnam',
    'BN': 'Brunei',
    'NZ': 'New Zealand',
    'MM': 'Myanmar',
    'KH': 'Cambodia',
    'MN': 'Mongolia',
    'LA': 'Laos',
    'PG': 'Papua New Guinea'
}

lc_dict = {
    np.nan: 'Active lifecycle',
    'EOL': 'End of life',
    'NPI': 'New product introduction',
    'RaMPDOWN': 'RaMPDOWN'
}




with st.sidebar:
    st.title("Welcome to SupplAi.")
    st.image("SupplAi logo.png")
    st.subheader("[Demo version] Powered by Hi35!")


st.header("Data selection")

m_i, m_f = st.select_slider("Select below the period on which the analysis run.",options=range(35),value=(0, 34), format_func = lambda i : months_raw[i])

months = months_raw[m_i:m_f+1]

st.markdown("The different tabs in the expander below allow you to filter the data used in the analysis.")

data_sel_expander = st.expander("Filters")
(
    country_filter,
    depot_center_filter,
    strategic_product_filter,
    life_cycle_filter
) = data_sel_expander.tabs(
    [
        "Country",
        "Depot distribution center",
        "Strategic product family",
        "Life cycle",
    ]
)


countries = country_filter.multiselect("Select the enabled countries", country_dic.keys(),
                           format_func=lambda i : country_dic[i], default=country_dic.keys())

df_countries_filter = df[df["Country"].isin(countries)]
av_centers = df_countries_filter["Site"].unique()

centers = depot_center_filter.multiselect("Select the enabled depot distribution centers", av_centers, default=av_centers)

df_center_filter = df_countries_filter[df_countries_filter["Site"].isin(centers)]
av_strategies = df_center_filter["Strategic Product Family proxy"].unique()

strategies = strategic_product_filter.multiselect("Select the strategic products families", av_strategies,
                            format_func=lambda i: "Family " + i.replace("Strategic Product Family-", ""),
                            default=av_strategies)

df_strategies_filter = df_center_filter[df_center_filter["Strategic Product Family proxy"].isin(strategies)]
av_lc = df_strategies_filter["Product Life cycel status"].unique()

lc = life_cycle_filter.multiselect("Select the strategic products families", av_lc,
                            format_func=lambda i: lc_dict[i],
                            default=av_lc)

df_lc_filter = df_strategies_filter[df_strategies_filter["Product Life cycel status"].isin(lc)]

final_df = df_lc_filter

st.header("Data prediction and analysis")

st.subheader("Sales evolution")

line = pd.DataFrame(final_df[months].sum()).rename(columns={0: 'Price'})
st.plotly_chart(px.line(line, title='Sales prediction', template='plotly'), theme=None, use_container_width=True)


pan_data = final_df.groupby("Country").sum()[months].sum(axis=1).reset_index().rename(columns={0: 'Sales'})

iso_alpha3_dic = {
    'DE': 'DEU',
    'CN': 'CHN',
    'GB': 'GBR',
    'AU': 'AUS',
    'ES': 'ESP',
    'NL': 'NLD',
    'US': 'USA',
    'DK': 'DNK',
    'BE': 'BEL',
    'FR': 'FRA',
    'IT': 'ITA',
    'PL': 'POL',
    'SE': 'SWE',
    'TW': 'TWN',
    'JP': 'JPN',
    'HK': 'HKG',
    'KR': 'KOR',
    'PH': 'PHL',
    'MY': 'MYS',
    'SG': 'SGP',
    'TH': 'THA',
    'Id': 'IDN',  # Correction du code 'Id' en 'IDN'
    'FJ': 'FJI',
    'VN': 'VNM',
    'BN': 'BRN',
    'NZ': 'NZL',
    'MM': 'MMR',
    'KH': 'KHM',
    'MN': 'MNG',
    'LA': 'LAO',
    'PG': 'PNG'
}

pan_data["Country"] = pan_data["Country"].apply(lambda t : iso_alpha3_dic[t])
fig = px.choropleth(pan_data, locations="Country",
                    color="Sales", # lifeExp is a column of gapminder
                    hover_name="Country", # column to add to hover information
                    color_continuous_scale=["rgb(255,255,0)","rgb(255,0,0)"])
st.plotly_chart(fig)

st.subheader("Data distribution analysis")

st.markdown("The different tabs in the expander below allow you to explore the data distribution by different features.")

data_dis_expander = st.expander("Distribution analysis")

feature_dis_analysis = data_dis_expander.selectbox("Select feature (choose None for optimisation)", [
        "None",
        "Country",
        "Strategic product analysis",
        "Life cycle analysis",
    ])

col1, col2 = data_dis_expander.columns(2)

if feature_dis_analysis == "Country":
    pan_data = final_df.groupby("Country").sum()[months].sum(axis=1).reset_index().rename(columns={0: 'Sales'})
    pan_data['Country'] = pan_data['Country'].apply(lambda i: country_dic[i])
    col1.plotly_chart(px.pie(pan_data, values='Sales', names='Country', template='plotly'), use_container_width=True,
                      theme=None)
    col2.plotly_chart(px.histogram(pan_data, y='Sales', x='Country', template='plotly'), use_container_width=True,
                      theme=None)

if feature_dis_analysis == "Strategic product analysis":
    pan_data = final_df.groupby("Strategic Product Family proxy").sum()[months].sum(axis=1).reset_index().rename(
        columns={0: 'Sales'})
    pan_data["Strategic Product Family proxy"] = pan_data["Strategic Product Family proxy"].apply(
        lambda i: "Family " + i.replace("Strategic Product Family-", ""))
    col1.plotly_chart(px.pie(pan_data, values='Sales', names="Strategic Product Family proxy", template='plotly'),
                      use_container_width=True, theme=None)
    col2.plotly_chart(px.histogram(pan_data, y='Sales', x="Strategic Product Family proxy", template='plotly'),
                      use_container_width=True, theme=None)

if feature_dis_analysis == "Life cycle analysis":
    pan_data = final_df.groupby("Product Life cycel status").sum()[months].sum(axis=1).reset_index().rename(
        columns={0: 'Sales'})
    pan_data['Product Life cycel status'] = pan_data['Product Life cycel status'].apply(lambda i: lc_dict[i])
    col1.plotly_chart(px.pie(pan_data, values='Sales', names='Product Life cycel status', template='plotly'),
                      use_container_width=True, theme=None)
    col2.plotly_chart(px.histogram(pan_data, y='Sales', x='Product Life cycel status', template='plotly'),
                      use_container_width=True, theme=None)

# df_strategies_filter[].sum()