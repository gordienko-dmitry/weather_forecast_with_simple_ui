# Mini server for weather forecast  
**Made for [ycloud.school](ycloud.school)**  
Test exercise with weather forecast with advices (third level).  
Using **Python**, **Aiohttp**, and **html page** as UI.    

#### Using:
* [wttr.in](http://wttr.in/) API for weather forecast. [More info here...](https://github.com/chubin/wttr.in)  
* [bootstrap](https://getbootstrap.com/) for frontend part.

![Screenshot image](media/screen.png)

### Install
First of all, install Python3 (version 3.8 or above).  
Then clone this repository or download it in archive.
  
After it install requirements with your terminal and pip command:  
```bash
pip install -r requirements.txt
```  

### Run
For running script type in your terminal  
```bash
python server.py
```  


#### How it works  
* User enter town (or country, or other place, or coordinates, etc) and press button.
* Sends get query via ajax to server
* Server making 2 get queries to wttr: 
    - json response analyzing for advices
    - html response using for forecast visualization  
* Then results merges to html response  
* Page getting response and put it in div block   

That's it.    


**P.S.** If we have problem with get query we can see error message instead forecast visualization.  
 
 #### Video demonstration  
 Sorry, but for watch this video you need download it from media folder  
 
 
[![Demonstration video](media/video_screen.png)](media/demonstration.mp4)
