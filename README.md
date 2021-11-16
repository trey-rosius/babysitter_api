### What is the BabySitter App all about

## The Problem

So COVID came by and made Remote work possible. Yay!!!. Now it's possible to work in our pyjamas from our bedrooms,sipping coffee from that large Mug we've always dreamt of. I don't know about you, but to me, working like this is a dream come true.
<br />
<br />
But now, the noise 🥲.
<br />
<br />
Most of us are parents. For some sweet reason, our kids always decide to show how much they love us, during zoom meetings.
<br />
<br />
They're either banging on the closed door or creating some noise with stuff from outside, because there's nobody to sit and put them in order.
<br />
<br />
There has to be a solution to this 🤔. Yeahhhh... Get a nanny.But then, issues come in.
<br />

- Firstly, where or how do you meet this nanny ?

- Supporsing you meet them ,are you comfortable leaving your kids with somebody you don't know ?

- How do you evaluate the them to know if they are a good fit for your kids ?

- How can you speak to other people that have worked with them in the past ?
  <br />
  And a ton of other questions.

What if there's an online website just for stuff like this. Where you can see people willing to carryout nanny duties.
<br />
They are a ratings and feedback system, and you can actually see reviews from previous jobs they've done.
<br />
<br />
That's the main purpose of this Project.
<br />
I'll attempt to create an `Event Driven Application`, based on this use Case.
<br />

## The Solution

This REPO would contain all the code for the serverless GraphQL API.

### ENTITIES

#### User Type

Starting off with a simple structure, i'll assume there are only 3 types of users

- Admins
- Parents(Single or Couple)
- Nannys

#### JOB POSTING

- Parents can put up a job posting like(We need a somebody, aged between 21 and 40 to look after our son everyday from 8AM to 6PM.
- Job Type
- schedule(Time and Date)
- Location
- Number of Kids
- Cost

#### User Profiles

##### Nanny

- Full Names
- Date of Birth
- Gender
- Spoken languages
- Current Location
- Nationality
- Region of Origin
- National ID Card or Some Kind of identification
- Phone Number(Just of verification)
- Profile Picture
- Hourly Rate
- Level of Education
- Smoke/drink etc
- Any Disability
- Brief Description
- List of activities they can do

##### Parents

- Full Names
- Location
- Date of Birth
- Phone Number(Just for Verification)
- List of Job postings

##### Admins

#### Ratings and Reviews

##### Nannys

- Answer a set of questions based on their experience with a Parent.
- Leave a brief review
- Leave a rating

##### Parents

- Answer a set of questions based on their experience with a Nanny.
- Leave a brief review
- Leave a rating

Reviews/Ratings will be publicly vissible on each users profile.

#### Chats

Parent

### STACK

- GraphQL
- Python
- EventBridge for Events
- SQS for Queueing
- SNS for Notifications
- SES for Emails
- SAM(IaC)

### SERVICES

- User
- Jobs
- Notification
- Ratings/Reviews
- Chats

### How's this solution supposed to work
- Register/Log Into the App
- Create/Update User Profile
- For Nanny's, See List of Job Postings
- For Parents, see the list of Nanny's,  highest rated first.
- Parents should be a ble to 

<br />