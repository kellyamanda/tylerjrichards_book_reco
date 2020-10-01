import streamlit as st
import numpy as np
import pandas as pd
import xmltodict
from pandas.io.json import json_normalize
import urllib.request
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
import gender_guesser.detector as gender

st.beta_set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

# image = Image.open('books.jpg')
# st.image(image, use_column_width=True)

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((.1,2,.2,1,.1))

with row0_1:
    st.title('Analyzing Your Goodreads Reading Habits')
with row0_2:
    st.write('')
    st.subheader('A Web App by Tyler Richards')

row1_spacer1, row1_1, row1_spacer2 = st.beta_columns((.1,3.2,.1))

with row1_1:
    st.markdown("Hey there! Welcome to Tyler's Goodreads Analysis App. This app scrapes (and never keeps or stores!) the books you've read and analyzes data about your book list, including estimating the gender breakdown of the authors, and looking at the distribution of the age and length of book you read. After some nice graphs, it tries to recommend a curated book list to you from a famous public reader, like Barack Obama or Bill Gates. Give it a go!")
    st.markdown("**To begin, please enter the link to your [Goodreads profile](https://www.goodreads.com/) (or just use mine!).** 👇")

row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer2 = st.beta_columns((.1,2,.2,1,.1))

with row2_1:
    user_input = st.text_input("Input Goodreads Link", 'https://www.goodreads.com/user/show/89659767-tyler-richards')

with row2_2:
    need_help = st.beta_expander('Need help? 👉')
    with need_help:
        st.markdown("<sub><sup>Having trouble finding your Goodreads profile? Head to the [Goodreads website](https://www.goodreads.com/) and click profile in the top right corner.</sup></sub>",unsafe_allow_html=True)

user_id = ''.join(filter(lambda i: i.isdigit(), user_input))
user_name = user_input.split(user_id, 1)[1].split('-', 1)[1].replace('-', ' ')


@st.cache
def get_user_data(user_id, key = 'ZRnySx6awjQuExO9tKEJXw', v = '2', shelf = 'read', per_page = '200'):
	api_url_base = 'https://www.goodreads.com/review/list/'
	final_url = api_url_base + user_id + '.xml?key=' + key + '&v=' + v + '&shelf=' + shelf + '&per_page=' + per_page
	contents = urllib.request.urlopen(final_url).read()
	return(contents)

user_input = str(user_input)
contents = get_user_data(user_id=user_id, v = '2',
	shelf = 'read', per_page='200')
contents = xmltodict.parse(contents)
df = json_normalize(contents['GoodreadsResponse']['reviews']['review'])
u_books = len(df['book.id.#text'].unique())
u_authors = len(df['book.authors.author.id'].unique())
df['read_at_year'] = [i[-4:] if i != None else i for i in df['read_at']]


line1_spacer1, line1_1, line1_spacer2 = st.beta_columns((.1,3.2,.1))

with line1_1:
    st.markdown('***')
    st.header('Analyzing the Reading History of: **{}**'.format(user_name))

row3_space1, row3_1, row3_space2, row3_2, row3_space3, row3_3, row3_space4 = st.beta_columns((.1,1,.1,1,.1,1,.1))

with row3_1:
    year_df = pd.DataFrame(df['read_at_year'].value_counts()).reset_index()
    sns.barplot(x = year_df['index'], y = year_df['read_at_year'], color='goldenrod')
    plt.xlabel('Year')
    plt.ylabel('Books Read')
    st.subheader('Books Read')
    st.pyplot()
    st.markdown("It looks like you've read a grand total of **{} books with {} authors,** with {} being your most read author! That's awesome. Here's what your reading habits look like since you've started using Goodreads.".format(u_books, u_authors, df['book.authors.author.name'].mode()[0]))

# st.markdown("We're going to use the Goodreads API, along with some other data, to analyze your reading habits and then try to recommend some book lists or readers. We'll start with the age distribution of your read books, move on to a ratings analysis, and also look at the popularity of the books that you choose. Let's get started!")

with row3_2:
    st.subheader("Book Age")
    # st.markdown("This next graph starts with the distribution of publication date for your read books. I've always wanted to try and read books that stand the test of time, and this graph let's me see how I do on that axis.")
    sns.distplot(pd.to_numeric(df['book.publication_year'], errors='coerce').dropna().astype(np.int64), kde_kws={'clip': (0.0, 2020)})
    plt.xlabel('Book Publication Year')
    st.pyplot()

    avg_book_year = str(int(np.mean(pd.to_numeric(df['book.publication_year']))))
    row = df[df['book.publication_year'] == str(pd.to_numeric(df['book.publication_year']).min())[0:4]]
    oldest_book = row['book.title_without_series'].iloc[0]
    row_young = df[df['book.publication_year'] == str(pd.to_numeric(df['book.publication_year']).max())[0:4]]
    youngest_book = row_young['book.title_without_series'].iloc[0]

    st.markdown("Looks like the average publication date is around **{}**, with your oldest book being **{}** and your youngest being **{}**.".format(avg_book_year, oldest_book, youngest_book))
    st.markdown("Note that the pubication date on Goodreads is the **last** publication date, so the data is altered for any book that has been republished by a publisher.")

    compare_age = st.beta_expander("Compare with average Goodreads distribution 👉")

    with compare_age:
        st.subheader("Book Rating Distribution")
        sns.distplot(pd.to_numeric(df['book.average_rating'], errors='coerce').dropna(), kde_kws={'clip': (0.0, 5.0)})
        plt.xlabel('Book Rating')
        st.pyplot()
        st.markdown("Here is the distribution of average rating by other Goodreads users for the books that you've read. Note that this is a distribution of averages, which explains the lack of extreme values!")
        st.write('')
        # st.markdown("Now let's compare that to how you've rated the books you've read.")

with row3_3:
    st.subheader("Book Rating Distribution")
    rating_df = pd.DataFrame(pd.to_numeric(df[df['rating'].isin(['1','2','3','4','5'])]['rating']).value_counts(normalize=True)).reset_index()
    sns.barplot(x=rating_df['index'], y = rating_df['rating'], color= "goldenrod")
    plt.ylabel('Percentage')
    plt.xlabel('Your Book Ratings')
    st.pyplot()

    df['rating_diff'] = pd.to_numeric(df['book.average_rating']) - pd.to_numeric(df[df['rating'].isin(['1','2','3','4','5'])]['rating'])

    difference = np.mean(df['rating_diff'].dropna())
    row_diff = df[abs(df['rating_diff']) == abs(df['rating_diff']).max()]
    title_diff = row_diff['book.title_without_series'].iloc[0]
    rating_diff = row_diff['rating'].iloc[0]
    pop_rating_diff = row_diff['book.average_rating'].iloc[0]


    if difference > 0:
    	st.markdown("It looks like on average you rate books lower than the average Goodreads user, **by about {} points**. You differed from the crowd most on the book {} where you rated the book {} stars while the general readership rated the book {}".format(round(difference, 3), title_diff, rating_diff, pop_rating_diff))
    else:
    	st.markdown("It looks like on average you rate books higher than the average Goodreads user, **by about {} points**. You differed from the crowd most on the book {} where you rated the book {} stars while the general readership rated the book {}".format(round(difference, 3), title_diff, rating_diff, pop_rating_diff))

st.write('')
row4_space1, row4_1, row4_space2, row4_2, row4_space3, row4_3, row4_space4 = st.beta_columns((.1,1,.1,1,.1,1,.1))

with row4_1:
    #page breakdown
    st.subheader('Book Length Distribution')
    sns.distplot(pd.to_numeric(df['book.num_pages'].dropna()))
    st.pyplot()

    book_len_avg = round(np.mean(pd.to_numeric(df['book.num_pages'].dropna())))
    book_len_max = pd.to_numeric(df['book.num_pages']).max()
    row_long = df[pd.to_numeric(df['book.num_pages']) == book_len_max]
    longest_book = row_long['book.title_without_series'].iloc[0]

    st.markdown("Your average book length is **{} pages**, and your longest book read is **{} at {} pages!** Now let's move on to a gender breakdown of your authors.".format(book_len_avg, longest_book, int(book_len_max)))

with row4_2:
    st.subheader('Gender Breakdown')
    #gender algo
    d = gender.Detector()
    new = df['book.authors.author.name'].str.split(" ", n = 1, expand = True)

    df["first_name"]= new[0]
    df['author_gender'] = df['first_name'].apply(d.get_gender)
    df.loc[df['author_gender'] == 'mostly_male', 'author_gender'] = 'male'
    df.loc[df['author_gender'] == 'mostly_female', 'author_gender'] = 'female'


    author_gender_df = pd.DataFrame(df['author_gender'].value_counts(normalize=True)).reset_index()
    sns.barplot(x=author_gender_df['index'], y = author_gender_df['author_gender'], color= "goldenrod")
    plt.ylabel('Percentage')
    plt.xlabel('Gender')
    st.pyplot()
    st.markdown('To get the gender breakdown of the books you have read, this next bit takes the first name of the authors and uses that to predict their gender. These algorithms are far from perfect, and tend to miss non-Western/non-English genders often so take this graph with a grain of salt.')
    st.markdown("Note: the package I'm using for this prediction outputs 'andy', which stands for androgenous, whenever multiple genders are nearly equally likely (at some threshold of confidence). It is not, sadly, a prediction of a new gender called andy.")

with row4_3:
    st.subheader("Gender Distribution Over Time")
    year_author_df = pd.DataFrame(df.groupby(['read_at_year'])['author_gender'].value_counts(normalize=True))
    year_author_df.columns = ['Percentage']
    year_author_df.reset_index(inplace=True)
    year_author_df = year_author_df[year_author_df['read_at_year'] != '']
    sns.lineplot(x=year_author_df['read_at_year'], y=year_author_df['Percentage'], hue = year_author_df['author_gender'])
    plt.xlabel('Year')
    plt.ylabel('Percentage')
    st.pyplot()
    st.markdown('Here you can see the gender distribution over time to see how your reading habits may have changed.')


row5_spacer1, row5_1, row5_spacer2 = st.beta_columns((.1,3.2,.1))

with row5_1:
    st.write('')
    st.write('')
    st.header("Book List Recommendation for **{}**".format(user_name))

    reco_df = pd.read_csv('recommendations_df.csv')
    unique_list_books = df['book.title'].unique()
    reco_df['did_user_read'] = reco_df['goodreads_title'].isin(unique_list_books)
    most_in_common = pd.DataFrame(reco_df.groupby('recommender_name').sum()).reset_index().sort_values(by='did_user_read', ascending=False).iloc[0][0]
    avg_in_common = pd.DataFrame(reco_df.groupby('recommender_name').mean()).reset_index().sort_values(by='did_user_read', ascending=False).iloc[0][0]
    most_recommended = pd.DataFrame(reco_df.groupby('recommender').sum()).reset_index().sort_values(by='did_user_read', ascending=False).iloc[0][0]
    avg_recommended = pd.DataFrame(reco_df.groupby('recommender').mean()).reset_index().sort_values(by='did_user_read', ascending=False).iloc[0][0]

    def get_link(recommended):
        if '-' not in recommended:
            link = 'https://bookschatter.com/books/' + recommended
        elif '-' in recommended:
            link = 'https://www.mostrecommendedbooks.com/' + recommended + '-books'
        return(link)

    st.markdown('For one last bit of analysis, we scraped a few hundred book lists from famous thinkers in technology, media, and government (everyone from Barack and Michelle Obama to Keith Rabois and Naval Ravikant). We took your list of books read and tried to recommend one of their lists to book through based on information we gleaned from your list')
    st.markdown("You read the most books in common with **{}**, and your book list is the most similar on average to **{}**. Find their book lists [here]({}) and [here]({}) respectively".format(most_in_common, avg_in_common, get_link(most_recommended), get_link(avg_recommended)))

    st.markdown('***')
    st.markdown("Thanks for going through this mini-analysis with me! I'd love feedback on this, so if you want to reach out you can find me on [twitter] (https://twitter.com/tylerjrichards) or my [website](http://www.tylerjrichards.com/).")
