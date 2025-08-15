# agent_config.py
from pathlib import Path

AGENT_CONFIGS = {
    
    "aryan": {
        "agent_name":      "Aryan AI Agent",
        "agent_contact":   "9810467541",
        "prompt_template": "aryan_ai_agent_prompt",
        "projects": [
            {
                "project_key":   "unknown",
                "project_name":  "Aryan Projects",
                "context_path":  Path("data/agent-data/aryandata.txt"),
                "page_urls": [
                    "https://google.com"
                ],
                "default": True    # mark this as the fallback if no URL match
            },
            {
                "project_key":   "sg_daxin_vistas",
                "project_name":  "Signature Global Daxin Vistas",
                "context_path":  Path("data/agent-data/sgdaxindata.txt"),
                "page_urls": [
                    "https://daxinvistas.signatureglobalproject.com"
                ],
                "default": True    # mark this as the fallback if no URL match
            },
            {
                "project_key":   "sg_titanium_spr",
                "project_name":  "Signature Titanium SPR",
                "context_path":  Path("data/agent-data/sgtitaniumdata.txt"),
                "page_urls": [
                    "https://signatureglobalproject.com"
                ],
            },
            {
                "project_key":   "elan_the_presidential",
                "project_name":  "Elan The Presidential",
                "context_path":  Path("data/agent-data/elanthepresidentialdata.txt"),
                "page_urls": [
                    "https://elanpresidential.elanthepresidential106.info",
                    "https://realtyseek.ai/demo/elanthepresidential/",
                ],
                # no “default” here, so only used if URL matches
            },
            {
                "project_key":   "whl_the_aspen",
                "project_name":  "Whiteland The Aspen",
                "context_path":  Path("data/agent-data/whitelandtheaspendata.txt"),
                "page_urls": [
                    "https://whitelandprojects.live/whiteland-sector-76-gurgaon"
                ],
            },
            {
                "project_key":   "whl_westin_residencies",
                "project_name":  "Whiteland Westin Residencies",
                "context_path":  Path("data/agent-data/whitelandwestinresidenciesdata.txt"),
                "page_urls": [
                    "https://www.whitelandprojects.live/whiteland-103-gurugram"
                ],
            },
        ]
    },
    "elan": {
        "agent_name":      "Elan AI Agent",
        "agent_contact":   "9810467541",
        "prompt_template": "project_or_builder_agent_prompt",
        "projects": [
            {
                "project_key":   "elan_the_emperor",
                "project_name":  "Elan The Emperor",
                "context_path":  Path("data/agent-data/elantheemperor.txt"),
                "page_urls": [
                    "https://realtyseek.ai/demo/elantheemperor",
                    "https://elanlimited.com/projects/the-emperor"
                ],
                "default": True    # mark this as the fallback if no URL match
            },
            {
                "project_key":   "elan_the_presidential",
                "project_name":  "Elan The Presidential",
                "context_path":  Path("data/agent-data/elanthepresidential.txt"),
                "page_urls": [
                    "https://realtyseek.ai/demo/elanthepresidential/"
                ],
                # no “default” here, so only used if URL matches
            }
        ]
    },
    "sobha": {
        "agent_name":      "Sobha AI Agent",
        "agent_contact":   "9810467541",
        "prompt_template": "project_or_builder_agent_prompt",
        "projects": [
            {
                "project_key":   "sobha_altus",
                "project_name":  "Sobha Altus",
                "context_path":  Path("data/agent-data/sobha-altus.txt"),
                "page_urls": [
                    "https://realtyseek.ai/demo/sobha-altus"
                ],
                "default": True    # mark this as the fallback if no URL match
            }
        ]
    },
    # add more agents here...
    # "sobha": { ... },
}

# fallback if an unknown agent_key comes in
DEFAULT_AGENT = {
    "agent_name":      "RealtySeek AI",
    "agent_contact":   "",
    "prompt_template": "default_agent_prompt",
    "projects": [
        {
            "project_key":   "default",
            "project_name":  "",
            "context_path":  Path("data/agent-data/default.txt"),
            "page_urls":     [],
            "default":       True
        }
    ]
}
