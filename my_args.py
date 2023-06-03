from os import getenv


def vpc_arguments(parser):
    parser.add_argument(
        'tag',
        type=str,
        help="Tag which will be assigned to vpc."
    )

    parser.add_argument(
        "-c",
        "--create_vpc",
        help="flag to create vpc.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )
    
    parser.add_argument(
        "-igw",
        "--create_internet_gateway",
        help="flag to create internet gateway.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )
    
    parser.add_argument(
        "-aigw",
        "--attach_internet_gateway",
        help="flag to attach internet gateway to vpc.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )
    
    parser.add_argument(
        "-vi",
        '--vpc_id', 
        help="flag to provide vpc_id.",
        type=str
    )

    parser.add_argument(
        "-cvs",
        "--create__with_subnets",
        help="flag to create vpc with subnets.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )
    
    parser.add_argument(
        '-pu', 
        "--public_subnets",
        type=int, 
        help='number of public subnet')
    
    
    parser.add_argument(
        '-pr', 
        "--private_subnets",
        type=int, 
        help='number of private  subnet')
    
    parser.add_argument('-npr', type=int, help='number of private subnet')
    

    parser.add_argument(
        "-ump",
        "--upload_myauto_pictures",
        help="flag upload downloaded pictures.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )

    parser.add_argument(
        "-arp",
        "--assign_read_policy",
        help="flag to assign read bucket policy.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )

    parser.add_argument(
        "-lo",
        "--list_objects",
        type=str,
        help="list bucket object",
        nargs="?",
        const="True",
        default="False"
    )

    return parser
