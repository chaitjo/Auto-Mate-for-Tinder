import pynder
import os
import urllib

from nude import *
from rake import *


if __name__ == "__main__":
    facebook_id = ""                # insert fb login id here
    facebook_auth_token = ""        # insert fb authentication token here
    user_limit = input("\nNumber of tests: ")
    image_limit = input("Number of images per test: ")

    session = pynder.Session(facebook_id, facebook_auth_token)
    total_users = session.nearby_users()
    if len(total_users) > user_limit:
        users = total_users[:user_limit]
    else: users = total_users
    
    for user in users:
        print("\n----------\n\nRunning the promiscuity algorithm for " + user.name + ', ' + str(user.age))
        total_skin_percent = 0.0
        bio_score = 0.0
        final_percent = 0.0


        # Image analysis
        image_count = 0
        for image in user.get_photos(width='320'):
            if image_count < image_limit:
                image_count += 1
                image_name = 'temp'+str(image_count)+'.jpg'
                photo_url = str(image)        
                print('\nPhoto '+ str(image_count) + ':\n' + photo_url)
                image = urllib.URLopener()
                image.retrieve(photo_url, image_name)

                skin_percent = 100*contains_nudity(image_name)
                color_skin(image_name)      # for testing accuracy of nude.py
                print('Skin region percentage = ' + str(skin_percent))
                total_skin_percent += skin_percent
                #os.remove(image_name)
            else: break
            
        total_skin_percent /= image_count
        print('\nAverage skin region percentage = ' + str(total_skin_percent))
        

        # Bio analysis
        text = user.bio.lower().replace('\n','. ')
        rake = Rake("rake_res/SmartStoplist.txt")
        keywords = rake.run(text.lower())        # keywords -> list of tuples. Each element- (word, wordscore)  
        word_list = load_word_list("rake_res/WordList.txt")

        for element in keywords: 
            for word in word_list.keys():
                if (element[0] in word) or (word in element[0]):
                    if 'no' in element[0] or 'not' in element[0]:
                        bio_score += 1.0*word_list[word]*element[1]
                    else: 
                        bio_score -= 1.0*word_list[word]*element[1]  
                
        if bio_score > 100 : bio_score = 100
        
        print('\nBio: ' + text)
        print(keywords)
        print('Bio score = ' + str(bio_score))
        
        # Combining Image and Bio scores
        if bio_score != 0:
            final_percent = (total_skin_percent + bio_score)/2
        else:
            final_percent = total_skin_percent
        print('\nFinal Score = ' + str(final_percent))

        like = raw_input("Press 'L' to like: ")
        if like == 'L' or like == 'l' : user.like()
