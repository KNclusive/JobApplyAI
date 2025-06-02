#!/usr/bin/env python
# coding: utf-8

from typing import List, Optional
from pydantic import BaseModel, Field

class Education(BaseModel):
    institution: str
    degree: str
    major: str
    minor: Optional[str]
    start_year: str
    end_year: Optional[str] = None
    result: Optional[str] = None
    location: Optional[str] = None

class Experience(BaseModel):
    position: str
    company: str
    location: str
    work_type: str
    start_date: str
    end_date: Optional[str] = None
    current: bool = False
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

class Certification(BaseModel):
    name: str
    issuer: str
    date_obtained: str
    credential_id: Optional[str] = None

class ResearchWork(BaseModel):
    title: str
    institution: str
    start_date: str
    end_date: str
    description: str
    outcomes: List[str]

class Skills(BaseModel):
    skill: str
    skill_type: Optional[str]
    proficiency: Optional[str]

class Login(BaseModel):
    domain: str = Field(description="This field Hold information on domain for which the login details are.")
    user_name: str = Field(description="Username used to login")
    password: str = Field(description="Password Used to login")

class Resume(BaseModel):
    personal_info: dict = Field(
        default_factory=lambda: {
            "name": "Karan Nair",
            "address": "The Dormers, Snipe Avenue, Upper New-Castle, Galway",
            "visa_status": "STAMP 1G",
            "phone": "+353892084101",
            "linkedin": "https://www.linkedin.com/in/karannair99",
            "github": "https://github.com/KNclusive?tab=repositories"
        }
    )

    objective: str = Field(
        default="AI/ML Engineer with expertise in deep learning, NLP, and large language models, "
                "skilled in developing scalable AI solutions for data-driven decision-making and "
                "process optimization."
    )

    skills: List[Skills]
    experience: List[Experience]
    education: List[Education]
    certifications: List[Certification]
    research_work: List[ResearchWork]
    login: List[Login]

    def Resume_summary(self) -> str:
        """Format resume for LLM consumption"""
        sections = [
            f"Name: {self.personal_info['name']}",
            f"Location: {self.personal_info['address']}",
            f"Visa-Status: {self.personal_info['visa_status']}"
            f"Contact: {self.personal_info['phone']} | {self.personal_info['linkedin']} | {self.personal_info['github']}"
        ]

        #Add Objective
        sections.append("\nObjective:\n" + self.objective)

        # Add Skills
        sections.append("\nProfessional Skills:")
        temp_skill_holder = {}
        for sk in self.skills:
            temp_skill_holder.setdefault(sk.skill_type, []).append(sk.skill)

        for key, val_list in temp_skill_holder.items():
            sections.append(
                f"\n{key} - {', '.join(val_list)}"
            )

        # Add experience
        sections.append("\nProfessional Experience:")
        for exp in self.experience:
            duration = f"{exp.start_date} - {exp.end_date}" if exp.end_date else f"{exp.start_date} - Present"
            sections.append(
                f"\n{exp.position} @ {exp.company} ({duration})"
                f"\nLocation: {exp.location} @ {exp.work_type}"
                f"\nTechnologies: {', '.join(exp.technologies)}"
                f"\nAchievements:\n" + "\n".join(f"  • {ach}" for ach in exp.achievements)
            )

        # Add education
        sections.append("\nEducation:")
        for edu in self.education:
            duration = f"{edu.start_year} - {edu.end_year}" if edu.end_year else str(edu.start_year)
            sections.append(
                f"\n{edu.degree} Majoring in {edu.major} and Minoring in {edu.minor}" if edu.minor else f"\n{edu.degree} Majoring in {edu.major}"
                f"\n{edu.institution} ({duration})"
                f"\nResult: {edu.result}"
            )

        # Add Certificates
        sections.append("\nCertification:")
        for ci in self.certifications:
            sections.append(
                f"\nTitle: {ci.name}"
                f"\nIssuing Organisation: {ci.issuer}"
                f"\nIssue Date: {ci.date_obtained}"
                f"\nCredential ID: {ci.credential_id}" if ci.credential_id else f"Produced on Request"
            )

        # Add Reserach-Work
        sections.append("\nResearch Work:")
        for rw in self.research_work:
            sections.append(
                f"\nTitle: {rw.title}"
                f"\nInstitution: {rw.institution}"
                f"\nDescription: {rw.description}"
            )

        return "\n".join(sections)

    def to_json(self) -> str:
        """Serialize for LLM agent consumption"""
        return self.model_dump_json(indent=2)

    @classmethod
    def read_json(cls, json_data: str) -> 'Resume':
        """Deserialize from LLM storage format"""
        return cls.model_validate_json(json_data)

    def query_resume(self, query: str) -> dict:
        """Example agent interface"""
        if "login" in query.lower():
            return {
                "Domain": [log.domain for log in self.login],
                "Username": [log.user_name for log in self.login],
                "Password": [log.password for log in self.login]
            }
        elif "experience" in query.lower():
            return {
                "Summary": self.Resume_summary(),
                "Experience": {
                    "Position": [exp.position for exp in self.experience],
                    "Company": [exp.company for exp in self.experience]
                }
            }
        elif "education" in query.lower():
            return {
                "Summary": self.Resume_summary(),
                "Education": {
                    "Institution": [edu.institution for edu in self.education],
                    "Degree": [edu.degree for edu in self.education],
                    "Major": [edu.major for edu in self.education]
                }
            }
        elif "personal details" in query.lower():
            return {
                "Summary": self.Resume_summary(),
                "Personal Information": {
                    "Name": [pi.name for pi in self.personal_info],
                    "Address": [pi.address for pi in self.personal_info],
                    "Visa_Status": [pi.visa_status for pi in self.personal_info],
                    "Phone": [pi.phone for pi in self.personal_info],
                    "Linkedin": [pi.linkedin for pi in self.personal_info],
                    "Github": [pi.github for pi in self.personal_info]
                }
            }
        elif "certificates" in query.lower():
            return {
                "Summary": self.Resume_summary(),
                "Certifications": {
                    "Name": [cf.name for cf in self.certifications],
                    "Issuing-Organisation": [cf.issuer for cf in self.certifications]
                }
            }
        elif "research" in query.lower():
            return {
                "Summary": self.Resume_summary(),
                "Research Works": {
                    "Title": [rw.title for rw in self.research_work],
                    "Institution": [rw.institution for rw in self.research_work]
                }
            }
        elif "skills" in query.lower():
            return {
                "Summary": self.Resume_summary(),
                "Skills": {
                    "Skill": [ts.skill for ts in self.skills],
                    "Skill Type": [ts.skill_type for ts in self.skills]
                }
            }
        elif "objective" in query.lower():
            return {
                "Objective": self.objective
            }
        else:
            return {
                "error": "No relevant data found"
            }