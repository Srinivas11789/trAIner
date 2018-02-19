# trAIner 

### Inspiration
We were inspired by the lack of aids in the fitness industry that provide the user with real time help with improving their form when doing exercises. So, we decided to built trAIner, which utilizes both haptic feedback, a web application and a companion mobile application to provide users with real time data on their exercises and to encourage users to continue to exercise by giving helpful tips to improve their posture.

### What it does
While you're doing certain body-weight exercises we offer two times of real-time feedback to help a person maintain proper form. The first is a mobile app that tells you a score each time you do a rep - and gives you comments on where you can fix your form. The second is an IoT connected vibration device that nudges you based on you mis-aligned your spine is as you do a rep of an exercise.

### How I built it
We built this app by dividing the workload into three parts. (1) Gathering data from a CV module and communicating it with our IoT Pi device, (2) processing and transforming data from seemingly arbitrary numbers to readable data, and (3) displaying the data on our front-end via mobile applications and web applications.

### Challenges I ran into
Srinivas - It has was hard to fetch the right angles for the inputs, and handling the back-end server for the web client, mobile applications, and IoT devices. Jeane - My biggest challenge was jumping into new data visualization tools. It was important for me not to just use cool, fancy technology but to actually explain a story with our data. I dug through a ton of documentation on d3.js, chart.js, and various other JS and CSS libraries. I was able to learn a lot through that! Liam - Determining back curvature was really difficult because the CV library we were using gave us access to certain joints only.
