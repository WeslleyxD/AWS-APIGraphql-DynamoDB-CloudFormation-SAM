# API Graphql Autenticada

## - Descrição
API Graphql autenticada por Key consumindo uma tabela do DynamoDB utilizando Infraestrutura como Código via Cloud Formation (AWS SAM).

## - Serviços Utilizados
- Appsync
- DynamoDB
- SAM
- Cloud Formation

## - Demonstração
[Screencast from 13-09-2022 20:41:28.webm](https://user-images.githubusercontent.com/93230531/190028801-eb2aac55-8857-43ae-a35c-317d4bd1bd58.webm)

## - Template.yaml
```yamlAWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
  appsync-authentication

Parameters:
  Region:
    Type: String
    Default: us-west-2
    Description: Region-Name

Resources:
  #ROLE AppsyncAuthentication
  AppsyncAuthenticationDynamoDBRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - appsync.amazonaws.com
            Action:
              - 'sts:AssumeRole'
      Policies:
        - PolicyName: dynamodb-access
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: "Allow"
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource: 
                  - !GetAtt StudentsTable.Arn

  #APPSYNC
  AppsyncAuthentication:
    Type: AWS::AppSync::GraphQLApi
    Properties:
      AuthenticationType: API_KEY
      Name: TestAPI

  AppsyncAuthenticationApiKey:
    Type: AWS::AppSync::ApiKey
    Properties: 
      ApiId: !GetAtt AppsyncAuthentication.ApiId
      Description: ApiKey do TestAPI
  
  AppsyncAuthenticationDataSource:
    Type: AWS::AppSync::DataSource
    Properties:
      ApiId: !GetAtt AppsyncAuthentication.ApiId
      Name: !Ref StudentsTable
      Type: AMAZON_DYNAMODB
      ServiceRoleArn: !GetAtt AppsyncAuthenticationDynamoDBRole.Arn
      DynamoDBConfig:
        AwsRegion: !Ref Region
        TableName: !Ref StudentsTable

  AppsyncAuthenticationSchema:
    Type: AWS::AppSync::GraphQLSchema
    Properties: 
      ApiId: !GetAtt AppsyncAuthentication.ApiId
      Definition: |
        type Query {
          getStudent(ID: ID!, Email: String): Student
          listStudents(limit: Int): StudentConnection
        }
        type Student {
          Email: String
          ID: ID!
        }
        type StudentConnection {
          items: [Student]
          nextToken: String
        }
        schema {
          query: Query
        }

  AppsyncAuthenticationResolver:
    Type: AWS::AppSync::Resolver
    Properties:
      ApiId: !GetAtt AppsyncAuthentication.ApiId
      TypeName: Query
      FieldName: getStudent
      DataSourceName: !GetAtt AppsyncAuthenticationDataSource.Name
      RequestMappingTemplate: >
        {
          "version": "2017-02-28",
          "operation": "GetItem",
          "key": {
            "ID": $util.dynamodb.toDynamoDBJson($ctx.args.ID),
            "Email": $util.dynamodb.toDynamoDBJson($ctx.args.Email),
          },
        }
      ResponseMappingTemplate: >
        $util.toJson($context.result)

  AppsyncAuthenticationResolverList:
    Type: AWS::AppSync::Resolver
    Properties:
      ApiId: !GetAtt AppsyncAuthentication.ApiId
      TypeName: Query
      FieldName: listStudents
      DataSourceName: !GetAtt AppsyncAuthenticationDataSource.Name
      RequestMappingTemplate: >
        {
          "version": "2017-02-28",
          "operation": "Scan",
          "filter": #if($context.args.filter) $util.transform.toDynamoDBFilterExpression($ctx.args.filter) #else null #end,
          "limit": $util.defaultIfNull($ctx.args.limit, 20),
          "nextToken": $util.toJson($util.defaultIfNullOrEmpty($ctx.args.nextToken, null)),
        }
      ResponseMappingTemplate: >
        $util.toJson($context.result)

  #DYNAMO
  StudentsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: Student
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: ID
          AttributeType: S
        - AttributeName: Email
          AttributeType: S
      KeySchema:
        - AttributeName: ID
          KeyType: HASH
        - AttributeName: Email
          KeyType: RANGE

  #LAMBDA
  AppsyncAuthenticationFunction:
    Type: AWS::Serverless::Function # More info about Function Resource: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Properties:
      CodeUri: appsync_authentication/
      Handler: app.lambda_handler
      Runtime: python3.9
      Environment:
        Variables:
          ApiKey: !GetAtt AppsyncAuthenticationApiKey.ApiKey
          ApiUrl: !GetAtt AppsyncAuthentication.GraphQLUrl

Outputs:
  AppsyncAuthenticationARN:
    Description: AppsyncAuthentication Arn
    Value: !GetAtt AppsyncAuthentication.Arn
  Student:
    Description: Student table created with this template
    Value: !GetAtt StudentsTable.Arn
```

## - TODO
Implementação Schema mutation