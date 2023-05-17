### Conclusion
<br />
We can keep going on and on, there's a ton of stuff to add to this api, to make it fully functional.
Here's a recap of everything we've covered thus far.

- Identified all entities and the relationships between them, plus access patterns required for the api.
- Proposed a solutions Architecture and gave a brief overview of all the
AWS services involved(Lambda,DynamoDB,SQS Queue,AppSync)
- Designed a single table schema, based on our access patterns
- Learnt the basics of IAM Roles and Policies.
- Secured our GraphQL schema using Cognito
- Created GraphQL endpoints for each entity and access patterns
- Used the `tracer` and `logger` functionalities of `aws-lambda-powertools` to effectively
monitor everything going on in our api.
- Used the newly released `batchItemFailure` mechanism of SQS to effectively scale the api

<br />

If you found this piece helpful, please spread the word. I'll love to know what you think.
If you find an error, please let me know and i'll be on it ASAP.
I enjoyed writing this tutorial, hope you enjoyed reading.
<br />

And that's all folks.
https://media.giphy.com/media/xUPOqo6E1XvWXwlCyQ/giphy.gif
