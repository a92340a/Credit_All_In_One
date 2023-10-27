# Credit_All_In_One
One-stop credit card information service including brief card introduction between Taiwan's banks, trending topics analysis from PPT community (One of Taiwan's largest forum) and easy-use question-answer retriever with chatbot

Website: https://credit-all-in-one.com

![Credit All-In-One Banner](https://34.120.182.71/banner.png)

## Table of Content
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
- [Data Model](#data-model)
- [Live Demo](#live-demo)
- [Real-time Monitoring](#real-time-monitoring)
- [Tools](#tools)


## Problem Statement
Eager to improve the time-consuming and inflexible search challenges posed by large-scale data


## Features
- **Brief card introduction** summerizes card information from official websites and blogs.
- **Trending topics analysis** generates graphs and recent hot articles from 'creditcard' board of PTT community.
- **Historical chatting records** shows latest 5 questions and answers for quick reviews.
- **Question-answer retriever with chatbot** utilizes OpenAI and LangChain to provide a conversational chatbot service.


## Architecture
### Overall Architecture
![Overall Architecture](https://34.120.182.71/personal_project5.png)

- Front-end:
    - Developed a Flask web service via Plotly graphing library, HTML, CSS (Bootstrap) and JavaScript.
    - Established a one-to-one channel using the Socket.IO protocol to maintain a long-term connection between the server and client to sequentially chat with bot.
- Back-end:
    - Designed a conversational model via OpenAI and LangChain, integrating a dataset of over 360 card contexts and applying two-step generative AI approach to enhance the accuracy of retrieving credit card names. More about conversational model see [LLM Architecture](#llm-architecture)
    - Conducted a Pub/Sub message queue for receiving a large volume of questions from users, and ensured horizontal scalability for accommodating multiple consumers.  
    
    - Implemented unit and integration tests to validate data transformation accuracy, and utilized GitHub Actions for continuous deployment, reducing the potential for human errors. 


### LLM Architecture
    
    - Implemented a two-step generative AI approach, involving inquiry-based and conversational models, to enhance the accuracy of retrieving credit card names.

## Data Pipeline and Data Model
    - Implemented an automated pipeline system to collect data utilizing ScrapeOps from 25 distinct sources, including official websites, blogs and PTT community.
    - Speeded up 3 data pipelines for querying credit card analysis by cache system, Redis, decreasing users’ waiting time by 20 seconds.



## Live Demo


## Real-time Monitoring 
Real-time logging and mo
    - Triggered spiders and monitored overall status of daily crawling pipelines through ScrapeOps scheduled jobs and dashboard.
    -  error handeling and notification

## Tools