from flask import Flask, redirect, render_template, request, session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key='abc'

GENRES = [
	"Action", "Adventure", "Animation", "Biography",
	"Comedy", "Crime", "Documentary", "Drama",
	"Family", "Fantasy", "History", "Horror",
	" ", "Mystery", "Romance", "Sci-Fi",
	"Sport", "Thriller", "War", "Western"
]


@app.route('/', methods=["GET", "POST"])
def index():
	#TODO
	#landing page
	if request.method == "POST":
		url = "https://www.imdb.com/search/title/?"

		titleType = request.form.getlist("title_type")
		#print(titleType)
		if titleType:
			url += "title_type="
			for i in range(len(titleType)):
				url += titleType[i] + ","

		genre = request.form.getlist("genres")
		#print(genre)
		if genre:
			url += "&genres="
			for i in range(len(genre)):
				url += genre[i] + ","

		dateMin = request.form.get("release_date-min")
		#print(dateMin)
		if dateMin:
			url += "&release_date=" + dateMin + ","

		dateMax = request.form.get("release_date-max")
		#print(dateMax)
		if dateMax:
			if dateMin:
				url += dateMax
			else:
				url += "&release_date=," + dateMax

		rateMin = request.form.get("user_rating-min")
		#print(rateMin)
		if rateMin:
			url += "&user_rating=" + rateMin + ","

		rateMax = request.form.get("user_rating-max")
		#print(rateMax)
		if rateMax:
			if rateMin:
				url += rateMax
			else:
				url += "&user_rating=," + rateMax

		group = request.form.getlist("groups")
		#print(group)
		if group:
			url += "&groups="
			for i in range(len(group)):
				url += group[i] + ","

		timeMin = request.form.get("runtime-min")
		#print(timeMin)
		if timeMin:
			url += "&runtime=" + timeMin + ","

		timeMax = request.form.get("runtime-max")
		#print(timeMax)
		if timeMax:
			if timeMin:
				url += timeMax
			else:
				url += "&runtime=," + timeMax

		#print(url)
		session['url'] = url
		page = request.form.get("page")

		return redirect(page)
	else:
		return render_template('index.html', genres=GENRES)

@app.route('/result')
def result():
	#TODO
	#result page
	url = session['url'] + "&count=250&&start={}&ref_=adv_nxt"
	#print(url)

	titles=[] #List to store name of the product
	years=[] #List to store price of the product
	ratings=[] #List to store rating of the product
	runtimes=[]
	certificates=[]
	genres=[]
	storylines=[]
	stars=[]

	pages = [1]
	i = 1
	#Initialise elements count in the page to 0
	elmcount = 0
	c=0
	x=0
	# For looping till the end of all elements in all pages, set while(i <= len(pages)) instead of while(i <= 1)
	while(i <= 1):
		driver.get(url.format(1+c))

		content = driver.page_source
		soup = BeautifulSoup(content, features="html.parser")
		for a in soup.findAll('div', attrs={'class':'lister-item-content'}):
			name=a.find('a', href=True)
			#print(name)
			year=a.find('span', attrs={'class':'lister-item-year'})
			#print(year)
			rating=a.find('strong')
			#print(rating)
			certificate=a.find('span', attrs={'class':'certificate'})
			runtime=a.find('span', attrs={'class':'runtime'})
			genre=a.find('span', attrs={'class':'genre'})
			storylist=[]
			stories=a.findAll('p', attrs={'class':'text-muted'})
			for story in stories:
				storylist.append(story.text)
	
			starslist=[]
			allstars=a.findAll('a', href=True)
			for star in allstars:
				starslist.append(star.text)
	
			if name:
				titles.append(name.text)
			else:
				titles.append("N/A")
			if year:
				years.append(year.text)
			else:
				years.append("N/A")
			if rating:
				ratings.append(rating.text)
			else:
				ratings.append("N/A")
			if runtime:
				runtimes.append(runtime.text)
			else:
				ratings.append("N/A")
			if certificate:
				certificates.append(certificate.text)
			else:
				certificates.append("N/A")
			if genre:
				genres.append((genre.text).strip())
			else:
				genres.append("N/A")
			if stories:
				storylines.append(storylist[1].strip())
				#print(storylist[1])
			else:
				storylines.append("N/A")
			if allstars:
				listToStr = starslist[-4:]
				finalstars = ', '.join(map(str, listToStr))

				stars.append(finalstars)
				#print(finalstars)
			else:
				stars.append("N/A")
	
	
	
			#df = pd.DataFrame({'Title':titles,'Year':years,'Rating':ratings,'Runtime':runtime, 'Certificate': certificates, 'Genres':genres, 'Storyline':storylines, 'Stars':stars}) #
			#df.to_csv('movies.csv', index=False, encoding='utf-8')
			#print(df.iloc[[x]])
			#print(tabulate(df.iloc[[x]], headers = 'keys', tablefmt = 'psql'))
			x += 1
	
	
	
		#Saving the default count of the page's elements.
		if i == 1:
			elmcount = len(soup.find_all('div', attrs={'class':'lister-item-content'}))

		i += 1
		c += len(soup.find_all('div', attrs={'class':'lister-item-content'}))
		#print(c)
		if c == 0:
			return render_template('nothing.html')
		#Comparing the count of the current page's elements with the default count, if it's less then it means this is the final page,
		#otherwise, move to the next page.
		if elmcount == (len(soup.find_all('div', attrs={'class':'lister-item-content'}))):
			pages.append(i)
	
	#print(str(len(pages)) + ' pages')
	
	return render_template('result.html', certificates=certificates, titles=titles, genres=genres, runtimes=runtimes, ratings=ratings, stars=stars, storylines=storylines, years=years)


@app.route('/lucky')
def lucky():
	#TODO
	#result page
	url = session['url'] + "&count=250&&start={}&ref_=adv_nxt" #&sort=user_rating,desc
	print(url)

	titles=[] #List to store name of the product
	years=[] #List to store price of the product
	ratings=[] #List to store rating of the product
	runtimes=[]
	certificates=[]
	genres=[]
	storylines=[]
	stars=[]

	pages = [1]
	i = 1
	#Initialise elements count in the page to 0
	elmcount = 0
	c=0
	x=0
	# For looping till the end of all elements in all pages, set while(i <= len(pages)) instead of while(i <= 1)
	while(i <= 1):
		driver.get(url.format(1+c))

		content = driver.page_source
		soup = BeautifulSoup(content, features="html.parser")
		for a in soup.findAll('div', attrs={'class':'lister-item-content'}):
			name=a.find('a', href=True)
			#print(name)
			year=a.find('span', attrs={'class':'lister-item-year'})
			#print(year)
			rating=a.find('strong')
			#print(rating)
			certificate=a.find('span', attrs={'class':'certificate'})
			runtime=a.find('span', attrs={'class':'runtime'})
			genre=a.find('span', attrs={'class':'genre'})
			storylist=[]
			stories=a.findAll('p', attrs={'class':'text-muted'})
			for story in stories:
				storylist.append(story.text)
	
			starslist=[]
			allstars=a.findAll('a', href=True)
			for star in allstars:
				starslist.append(star.text)
	
			if name:
				titles.append(name.text)
			else:
				titles.append("N/A")
			if year:
				years.append(year.text)
			else:
				years.append("N/A")
			if rating:
				ratings.append(rating.text)
			else:
				ratings.append("N/A")
			if runtime:
				runtimes.append(runtime.text)
			else:
				ratings.append("N/A")
			if certificate:
				certificates.append(certificate.text)
			else:
				certificates.append("N/A")
			if genre:
				genres.append((genre.text).strip())
			else:
				genres.append("N/A")
			if stories:
				storylines.append(storylist[1].strip())
				#print(storylist[1])
			else:
				storylines.append("N/A")
			if allstars:
				listToStr = starslist[-4:]
				finalstars = ', '.join(map(str, listToStr))

				stars.append(finalstars)
				#print(finalstars)
			else:
				stars.append("N/A")
	
	
	
			#df = pd.DataFrame({'Title':titles,'Year':years,'Rating':ratings,'Runtime':runtime, 'Certificate': certificates, 'Genres':genres, 'Storyline':storylines, 'Stars':stars}) #
			#df.to_csv('movies.csv', index=False, encoding='utf-8')
			#print(df.iloc[[x]])
			#print(tabulate(df.iloc[[x]], headers = 'keys', tablefmt = 'psql'))
			x += 1
	
	
	
		#Saving the default count of the page's elements.
		if i == 1:
			elmcount = len(soup.find_all('div', attrs={'class':'lister-item-content'}))

		i += 1
		c += len(soup.find_all('div', attrs={'class':'lister-item-content'}))
		print(c)
		if c == 0:
			return render_template('nothing.html')
		#Comparing the count of the current page's elements with the default count, if it's less then it means this is the final page,
		#otherwise, move to the next page.
		if elmcount == (len(soup.find_all('div', attrs={'class':'lister-item-content'}))):
			pages.append(i)
	
	#print(str(len(pages)) + ' pages')
	
	return render_template('lucky.html', certificates=certificates, titles=titles, genres=genres, runtimes=runtimes, ratings=ratings, stars=stars, storylines=storylines, years=years)