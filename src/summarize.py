import os

import cohere

API_KEY: str = os.environ.get("COHERE_API_KEY", "WZvnIklx8jzdruCvDlNFavJf3BN56rz5b9i6A5Q3")
print(API_KEY)

default_text = 'Passage: Is Wordle getting tougher to solve? Players seem to be convinced that the game has gotten harder '
'in recent weeks ever since The New York Times bought it from developer Josh Wardle in late January. The '
'Times has come forward and shared that this likely isn’t the case. That said, the NYT did mess with the '
'back end code a bit, removing some offensive and sexual language, as well as some obscure words There is a '
'viral thread claiming that a confirmation bias was at play. One Twitter user went so far as to claim the '
'game has gone to “the dusty section of the dictionary” to find its latest words.\nTLDR: Wordle has not '
'gotten more difficult to solve.\n\n--\n\nPassage: ArtificialIvan, a seven-year-old, London-based payment '
'and expense management software company, has raised $190 million in Series C funding led by ARG Global, '
'with participation from D9 Capital Group and Boulder Capital. Earlier backers also joined the round, '
'including Hilton Group, Roxanne Capital, Paved Roads Ventures, Brook Partners, and Plato Capital.\nTLDR: '
'ArtificialIvan has raised $190 million in Series C funding.\n\n--\n\nPassage: The National Weather Service '
'announced Tuesday that a freeze warning is in effect for the Bay Area, with freezing temperatures expected '
'in these areas overnight. Temperatures could fall into the mid-20s to low 30s in some areas. In '
'anticipation of the hard freeze, the weather service warns people to take action now.\nTLDR:',

text = """GitHub: Let’s build from here · GitHub Skip to content Toggle navigation Sign up Product Actions Automate 
any workflow Packages Host and manage packages Security Find and fix vulnerabilities Codespaces Instant dev 
environments Copilot Write better code with AI Code review Manage code changes Issues Plan and track work Discussions 
Collaborate outside of code Explore All features Documentation GitHub Skills Blog Solutions For Enterprise Teams 
Startups Education By Solution CI/CD & Automation DevOps DevSecOps Resources Learning Pathways White papers, Ebooks, 
Webinars Customer Stories Partners Open Source GitHub Sponsors Fund open source developers The ReadME Project GitHub 
community articles Repositories Topics Trending Collections Pricing Search or jump to Search code, repositories, 
users, issues, pull requests Search Clear Search syntax tips Provide feedback We read every piece of feedback, 
and take your input very seriously Include my email address so I can be contacted Cancel Submit feedback Saved 
searches Use saved searches to filter your results more quickly Name Query To see all available qualifiers, 
see our documentation  Cancel Create saved search Sign in Sign up You signed in with another tab or window Reload to 
refresh your session You signed out in another tab or window Reload to refresh your session You switched accounts on 
another tab or window Reload to refresh your session Dismiss alert {{ message }} GitHub Universe: Dive in to AI, 
security, and DevEx Get your tickets now to join us on Nov Let’s build from here The AI-powered developer platform to 
build, scale, and deliver secure software Email address Sign up for GitHub Start a free enterprise trial Trusted by 
the world’s leading organizations ↘︎ Productivity Collaboration Security Start a free enterprise trial Sign up for 
GitHub Productivity Accelerate high-quality software development Our AI-powered platform drives innovation with tools 
that boost developer velocityjson 1 2 3 4 5 6 7 8 9 10 11 12 < div class = " position-absolute width-full 
color-bg-default " style = " bottom : -4 rem ; " > < div class = " container-xl p-responsive " > < div class = " 
d-flex flex-justify-center flex-lg-justify-end color-bg-default " > < div class = " col-8 col-sm-7 col-md-6 col-lg-5 
position-relative z-2 right-lg-n12 events-none " > < picture > < source srcset = " astro-monawebp " type = " 
image/webp " > < img src = " astro-monasvg " width = " 960 " height = " 967 " class = " home-astro-mona width-full 
position-absolute bottom-0 height-auto " alt = " Mona looking at GitHub activity across the globe " > </ picture > </ 
div > </ div > </ div > </ div > Terminal Output Problems Debug Console [ 09:43:36 ] Starting ' 
watch-extension:vscode-api-tests '  [ 09:43:36 ] Finished ' clean-extension:typescript-language-features ' after 248 
ms [ 09:43:36 ] Starting ' watch-extension:typescript-language-features '  [ 09:43:36 ] Finished ' 
clean-extension:php-language-features ' after 384 ms [ 09:43:36 ] Starting ' watch-extension:php-language-features '  
[ 09:43:40 ] Finished ' clean-extension:html-language-features-server ' after 466 s [ 09:43:40 ] Starting ' 
watch-extension:html-language-features-server '  [ 09:43:43 ] Finished ' clean-client ' after 733 s [ 09:43:43 ] 
Starting ' watch-client '  GitHub Codespaces offers a complete dev environment in seconds, so you can code, build, 
test, and open pull requests from any repo anywhere Check out GitHub Codespaces Did you know? 22% increase in 
developer productivity after three years with GitHub 1 GitHub Copilot is your AI pair programmer that empowers you to 
complete tasks 55% faster by turning natural language prompts into coding suggestions Meet GitHub Copilot Python 
draw_scatterplotgo 1 2 3 4 5 6 7 8 import matplotlib  pyplot as plt def draw_scatterplot ( x_values , y_values ): plt 
 scatter ( x_values , y_values , s = 20 ) plt  title ( "Scatter Plot" ) plt  xlabel ( "x values" ) plt  ylabel ( "y 
 values" ) plt  show () Copilot Replay 1 2 3 4 5 6 7 const seconds = 3600 const minutes = seconds / 60 const hours = 
 minutes / 60 const days = hours / 24 const weeks = days / 7 const months = days / 30 const years = months / 12 
 Copilot Replay 1 2 3 4 5 6 7 8 9 10 11 package main func Memoize ( fn func ( int ) int ) func ( int ) int { cache := 
 make ( map [ int ] int ) return func ( n int ) int { if v , ok := cache [ n ]; ok { return v } cache [ n ] = fn ( n 
 ) return cache [ n ] } } Copilot Replay GitHub Actions automates your build, test, and deployment workflow with 
 simple and secure CI/CD Discover GitHub Actions GitHub Mobile fits your projects in your pocket, so you never miss a 
 beat while on the go Get GitHub Mobile Collaboration Supercharge collaboration We provide unlimited repositories, 
 best-in-class version control, and the world’s most powerful open source community—so your team can work more 
 efficiently together GitHub Issues and GitHub Projects supply flexible project management tools that adapt to your 
 team alongside your code Explore GitHub Issues Did you know? 80% reduction in onboarding time with GitHub 1 GitHub 
 Discussions create space to ask questions and have open-ended conversations Enable GitHub Discussions Pull requests 
 allow real-time communication and collaboration about code changes Check out pull requests GitHub Sponsors lets you 
 support your favorite open source maintainers and projects Invest with GitHub Sponsors Homebrew Sponsor curl Sponsor 
 CommandPost Sponsor Nick DeJesus Sponsor kazuya kawaguchi Sponsor Samuel Sponsor Nikema Sponsor sindresorhus Sponsor 
 Evan You Sponsor Security Embed security into the developer workflow With GitHub, developers can secure their code 
 in minutes and organizations can automatically comply with regulationsyml on: push Build 1m 21s Steps Initialize 
 CodeQL 1m 42s Autobuild 1m 24s Perform CodeQL Analyses 1m 36s GitHub Advanced Security lets you gain visibility into 
 your security posture, respond to threats proactively, and ship secure applications quickly Get GitHub Advanced 
 Security Did you know? 56 million projects fixed vulnerabilities with GitHub 2 Secret scanning automatically looks 
 for partner patterns and prevents fraudulent use of accidentally committed secrets Read about secret scanning 
 Dependabot makes it easy to find and fix vulnerable dependencies in your supply chain Explore Dependabot Code 
 scanning is GitHub’s static code analysis tool that helps you remediate issues in your code Download the latest SAST 
 ebook The place for anyone from anywhere to build anything Whether you’re scaling your startup or just learning how 
 to code, GitHub is your home Join the world’s largest developer platform to build the innovations that empower 
 humanity Let’s build from here Sign up for GitHub Start a free enterprise trial 1 The Total Economic Impact™ Of 
 GitHub Enterprise Cloud and Advanced Security, a commissioned study conducted by Forrester Consulting, 2022 Results 
 are for a composite organization based on interviewed customers 2 GitHub, Octoverse 2022 The state of open source 
 software Subscribe to The GitHub Insider Discover tips, technical guides, and best practices in our monthly 
 newsletter for developers Subscribe Product Features Enterprise Copilot Security Pricing Team Resources Roadmap 
 Compare GitHub Platform Developer API Partners Electron GitHub Desktop Support Docs Community Forum Professional 
 Services Premium Support Skills Status Contact GitHub Company About Customer stories Blog The ReadME Project Careers 
 Press Inclusion Social Impact Shop GitHub on X GitHub on Facebook GitHub on LinkedIn GitHub on YouTube GitHub on 
 Twitch GitHub on TikTok GitHub’s organization on GitHub © 2023 GitHub, Inc Terms Privacy ( Updated 08/2022 ) Sitemap 
 What is Git? You can’t perform that action at this time"""

co = cohere.Client(API_KEY)  # This is your trial API key
response = co.summarize(
    text=text,
    length='auto',
    format='bullets',
    model='command',
    additional_command='',
    temperature=0.8,
)
print('Summary:', response.summary)
