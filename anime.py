from urllib.request import urlopen as uReq
from urllib.error import HTTPError
from urllib.parse import quote
from bs4 import BeautifulSoup as soup
from tkinter import *
from PIL import ImageTk, Image
import io, requests, webbrowser


def recommend(profileName):
    global my_label
    global related
    global animeName
    global reco
    global e, myButton, root

    e.grid_forget()
    myButton.grid_forget()

    myurl = 'https://myanimelist.net/profile/' + profileName

    # Abre a pagina e faz download do HTML presente nela
    try:
        client = uReq(myurl)
    except HTTPError:
        main(error=True)

    pageHtml = client.read()
    client.close()

    # Analise do codigo em HTML
    profileSoup = soup(pageHtml, "html.parser")

    # Pega as caixas com informacoes
    favAnimeList = profileSoup.findAll("div", {"class": "fav-slide-outer"})
    try:
        favAnimes = favAnimeList[0].findAll("li", {"class": "btn-fav"})
    except IndexError:
        Label(root,text="You don't have any animes marked as favorite on myanimelist.com").pack()
        Label(root,text="Please add some and try again!").pack()
        return 0
    animeDict = dict()

    for animeIndex in range(0, len(favAnimes) - 1, 2):
#        print(f'\nIf you liked {favAnimes[animeIndex + 1].a.text} you might like...\n')
        link = favAnimes[animeIndex].a["href"]
        try:
            newClient = uReq(link)
        except UnicodeEncodeError:
            newLink = ''
            for char in link:
                if ord(char) > 128:
                    newLink += quote(char)
                else:
                    newLink += char
            newClient = uReq(newLink)

        newPageHtml = newClient.read()
        newClient.close()

        pageSoup = soup(newPageHtml, "html.parser")

        recommendations = pageSoup.findAll("a", {"class": "link bg-center ga-click"})

        for i, recommendation in enumerate(recommendations):
            smallImg = recommendation.img["data-src"]
            bigImg = 'https://cdn.myanimelist.net/images/' + smallImg[smallImg.find('anime/'):smallImg.find('?')]
            usersReco = recommendation.findAll("span", {"class": "users"})
#            print(usersReco)
            toAdd = [ImageTk.PhotoImage(
                Image.open(
                    io.BytesIO(
                        requests.get(
                            bigImg).content))), recommendation.span.text, recommendation["href"], usersReco[0].text,
                favAnimes[animeIndex + 1].a.text]
            if toAdd not in animeDict.values():
                animeDict[len(animeDict)] = toAdd

                #          print(recommendation.span.text)
#        print('-------------')


    # Start of the GUI
    def action(image_number):
        global my_label
        global related
        global animeName
        global button_forward
        global button_back
        global reco

        my_label.grid_forget()
        related.grid_forget()
        animeName.grid_forget()
        reco.grid_forget()
        my_label = Label(image=animeDict[image_number - 1][0])
        related = Label(root, text=f"If you liked {animeDict[image_number - 1][-1]}, you might like...", bg="#2e51a2", fg="white", height=3, width=40)
        animeName = Label(root, text='\n' + animeDict[image_number - 1][1], font=("Helvetica", 18))
        reco = Label(root, text="Recommended by " + animeDict[image_number-1][3].lower(), font=("Helvetica", 10))
        button_back = Button(root, text="<<", command=lambda: action(image_number - 1))
        if image_number >= len(animeDict):
            button_forward = Button(root, text=">>", command=lambda: action(1), bg="#2e51a2", fg="white")
        else:
            button_forward = Button(root, text=">>", command=lambda: action(image_number + 1), bg="#2e51a2", fg="white")
        if image_number <= 1:
            button_back = Button(root, text="<<", command=lambda: action(len(animeDict)), bg="#2e51a2", fg="white")
        else:
            button_back = Button(root, text="<<", command=lambda: action(image_number - 1), bg="#2e51a2", fg="white")
        button_MAL = Button(root, text="Why is this recommended?", command=lambda:
        webbrowser.open(animeDict[image_number-1][2]))
        button_player = Button(root, text="Watch this anime now!", command=lambda:
        webbrowser.open("https://gogoanime.ai//search.html?keyword=" + animeDict[image_number-1][1].replace(':', '')))

        my_label.grid(row=0, column=2, columnspan=2, rowspan=10)
        animeName.grid(row=1, column=0, columnspan=2)
        reco.grid(row=2, column=0, columnspan=2)
        related.grid(row=0, column=0, columnspan=2)
        button_back.grid(row=9, column=2)
        button_forward.grid(row=9, column=3)
        button_MAL.grid(row=9, column=0)
        button_player.grid(row=9, column=1)

    my_label = Label(image=animeDict[0][0])
    related = Label(root, text=f"If you liked {animeDict[0][-1]}, you might like...", bg="#2e51a2", fg="white", height=3, width=40)
    animeName = Label(root, text='\n' + animeDict[0][1], font=("Helvetica", 18))
    reco = Label(root, text="Recommended by "+animeDict[0][3].lower(), font=("Helvetica", 10))
    button_forward = Button(root, text=">>", command=lambda: action(2), bg="#2e51a2", fg="white")
    button_back = Button(root, text="<<", command=lambda: action(len(animeDict)), bg="#2e51a2", fg="white")
    button_MAL = Button(root, text="Why is this recommended?", command=lambda:
                        webbrowser.open(animeDict[0][2]))
    button_player = Button(root, text="Watch this anime now!", command=lambda:
                           webbrowser.open("https://gogoanime.ai//search.html?keyword="+ animeDict[0][1].replace(':', '')))

    my_label.grid(row=0, column=2, columnspan=2, rowspan=10)
    animeName.grid(row=1, column=0, columnspan=2)
    reco.grid(row=2, column=0, columnspan=2)
    related.grid(row=0, column=0, columnspan=2)
    button_back.grid(row=9, column=2)
    button_forward.grid(row=9, column=3)
    button_MAL.grid(row=9, column=0)
    button_player.grid(row=9, column=1)

    root.mainloop()


# Out of for loop: first input
def main(error=False):
    global e, myButton, root

    if not error:
        root = Tk()
    root.title("MAL recommendations")
#    root.iconbitmap('icon.ico')

    e = Entry(root, width=35, borderwidth=3)
    e.grid(row=0, column=0)
    if error:
        e.insert(0, "Please enter a valid username")
    else:
        e.insert(0, "My Anime List Username:")

    myButton = Button(root, text="See recommended animes", command=lambda: recommend(e.get()))
    myButton.grid(row=1, column=0)

    root.mainloop()


main()
