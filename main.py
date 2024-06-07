import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from io import StringIO


def site_info():
    with st.expander('Информация о сайте'):
        st.markdown('**О чем этот сайт?**')
        st.info('Об доходах различных жанров кино')
        st.markdown('**Как пользоваться этим сайтом?**')
        st.warning(
            'Чтобы использовать приложение, '
            '1. Выберите интересующие вас жанры в раскрывающемся списке.'
            '2. Выберите годы в виджете-ползунке.')


def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file), '.csv'
        elif file.name.endswith('.json'):
            return pd.read_json(file), '.json'
    except Exception as e:
        print(e)
        return None, None


def genre_selection(df):
    genres_list = df.genre.unique()
    genres_selection = st.multiselect('Выбрать жанры', genres_list,
                                      ['Боевик', 'Приключения', 'Военные', 'Комедия', 'Драма', 'Хоррор'])
    return genres_selection


def year_selection(df):
    year_list = df.year.unique()
    year_selection = st.slider('Выбрать годы', 1986, 2006, (2000, 2016))
    year_selection_list = list(np.arange(year_selection[0], year_selection[1] + 1))
    return year_selection_list


def plot_chart(df):
    reshaped_df = df.pivot_table(index='year', columns='genre', values='gross', aggfunc='sum', fill_value=0)
    reshaped_df = reshaped_df.sort_values(by='year', ascending=False)
    df_chart = pd.melt(reshaped_df.reset_index(), id_vars='year', var_name='Жанры', value_name='gross')

    chart = alt.Chart(df_chart).mark_line().encode(
        x=alt.X('year:N', title='Год'),
        y=alt.Y('gross:Q', title='Доход ($)'),
        color='Жанры:N'
    ).properties(height=320)
    st.altair_chart(chart, use_container_width=True)


def data_info(df):
    column_1, column_2 = st.columns(2)
    st.write("## Информация о данных")
    with column_1:
        st.write("Краткий обзор загруженных данных:")
        st.write(df.head())
        st.write("Полная информация данных")
        st.write(df)
    with column_2:
        st.write("Описательная статистика")
        st.write(df.describe())
        st.write("Таблица")
        buffer = StringIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue())


def main():
    st.set_page_config(page_title='Интерактивный проводник данных', page_icon='📊')
    st.title('📊 Интерактивный проводник данных')

    site_info()

    uploaded_file = st.file_uploader("Выберите файл для загрузки", type=['csv', 'json'])
    if uploaded_file is not None:
        df, file_type = load_data(uploaded_file)
        data_info_button = st.button("Информация о данных")
        redact_info = st.button("Редактирование данных")
        if data_info_button:
            data_info(df)
        elif redact_info:
            edit_data(df)
        else:
            genres_selection = genre_selection(df)
            year_selection_list = year_selection(df)
            df_selection = df[df.genre.isin(genres_selection) & df['year'].isin(year_selection_list)]
            plot_chart(df_selection)


def edit_data(df):
    column_3, column_4 = st.columns(2)
    st.write("## Редактирование данных")
    with column_3:
        st.write("Текущие данные:")
        st.write(df)
    with column_4:
        st.write("Измените данные:")
        disabled_columns = ['year']
        edited_df = st.data_editor(df, height=212, use_container_width=True,
                                   disabled=disabled_columns,
                                   num_rows="dynamic")

    if st.button("Сохранить изменения"):
        df.update(edited_df)
        st.success("Изменения сохранены успешно.")


if __name__ == "__main__":
    main()
