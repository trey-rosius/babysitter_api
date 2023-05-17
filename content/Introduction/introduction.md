### INTRODUCTION
We'll be using [AWS AppSync](https://aws.amazon.com/appsync/) to build out our api. AWS AppSync is a fully managed service allowing developers to deploy scalable GraphQL backends on AWS.
<br />
It's flexibility lets you utilize new or existing tables, using either a single-table design or a multi-table approach.
<br />
This api uses the single table design approach.In a single table design, all our entities would be stored
in the same DynamoDB table. This let's us perform multiple queries on different entities in
the same requests,that leads to a high efficiency as your app grows bigger.
<br />
<br />
This design approach has it's pros and cons, with one major con being the steep learning curve of modelling the
single table. It requires you to know and understand your access patterns properly beforehand.
<br />
<br />
Here are the concepts we'll be covering in this article.
<br />
- We'll use Appsync to improve security and incorporate different access patterns
- We'll Implement Single Table Design.
- We'll be using [aws lambda powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/) for tracing, structured logging, custom metrics and routing to properly
route all Graphql endpoints.
- Build faster with the new SAM Cli (`sam sync --stack-name`)

We already highlighted our use case above. Now, let's dive into our DynamoDB table Design.
