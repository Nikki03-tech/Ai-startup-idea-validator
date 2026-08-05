def generate_gtm_strategy(startup_name, industry, target_audience):

    if industry.lower() == "healthcare":
        pricing = [
            "Free Trial",
            "₹499/month",
            "₹999 Premium"
        ]

        channels = [
            "LinkedIn",
            "Hospital Partnerships",
            "Medical Conferences"
        ]

    elif industry.lower() == "education":
        pricing = [
            "Free Student Plan",
            "₹299/month",
            "Institution License"
        ]

        channels = [
            "Instagram",
            "Campus Ambassadors",
            "YouTube"
        ]

    elif industry.lower() == "fitness":
        pricing = [
            "7-Day Free Trial",
            "₹599/month",
            "₹999 Premium"
        ]

        channels = [
            "Instagram",
            "Fitness Influencers",
            "Referral Program"
        ]

    else:
        pricing = [
            "Free Trial",
            "Basic Plan",
            "Premium Plan"
        ]

        channels = [
            "Google Ads",
            "LinkedIn",
            "Referral Program"
        ]

    return {
        "startup_name": startup_name,
        "industry": industry,
        "target_audience": target_audience,
        "positioning": f"{startup_name} provides innovative {industry} solutions for {target_audience}.",
        "pricing": pricing,
        "customer_acquisition": channels,
        "launch_strategy": [
            "Build MVP",
            "Invite Beta Users",
            "Collect Feedback",
            "Official Launch"
        ]
    }