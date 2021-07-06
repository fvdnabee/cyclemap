# AWS ECR Public IAM policy
Github AWS user has the following IAM policy attached:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ecr-public:DescribeImageTags",
                "ecr-public:DescribeImages",
                "ecr-public:InitiateLayerUpload",
                "ecr-public:DescribeRepositories",
                "ecr-public:UploadLayerPart",
                "ecr-public:PutImage",
                "ecr-public:TagResource",
                "ecr-public:CompleteLayerUpload",
                "ecr-public:BatchCheckLayerAvailability"
            ],
            "Resource": "arn:aws:ecr-public::184611879143:repository/cyclemap"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ecr-public:GetAuthorizationToken",
                "sts:GetServiceBearerToken"
            ],
            "Resource": "*"
        }
    ]
}
```

# AWS ECS update service IAM policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ecs:UpdateService",
            "Resource": "arn:aws:ecs:eu-west-1:184611879143:service/cyclemap-tf/cyclemap-web"
        }
    ]
}
```

# TODO
Move these policies into the terraform repo, together with the creation of the
Github user and assigning the policies.
