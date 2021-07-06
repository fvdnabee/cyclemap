# AWS ECR Public AMI policy
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
