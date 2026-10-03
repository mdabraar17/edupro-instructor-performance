import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EduPro Instructor Performance", layout="wide")

@st.cache_data
def load():
    return (
        pd.read_excel("EduPro_Instructor_Course_Analysis.xlsx","Teachers"),
        pd.read_excel("EduPro_Instructor_Course_Analysis.xlsx","Courses"),
        pd.read_excel("EduPro_Instructor_Course_Analysis.xlsx","Leaderboard"),
        pd.read_excel("EduPro_Instructor_Course_Analysis.xlsx","Expertise_Analysis")
    )

teachers,courses,leaderboard,expertise = load()
st.title("EduPro — Instructor Performance & Course Quality")
st.caption("Synthetic dataset for academic/project demonstration")

st.sidebar.header("Filters")
exp = st.sidebar.multiselect("Expertise",sorted(teachers.Expertise.unique()))
cat = st.sidebar.multiselect("Course Category",sorted(courses.CourseCategory.unique()))
level = st.sidebar.multiselect("Course Level",sorted(courses.CourseLevel.unique()))
rating = st.sidebar.slider("Teacher Rating",0.0,5.0,(0.0,5.0),0.1)

ft = teachers[teachers.TeacherRating.between(*rating)]
if exp: ft=ft[ft.Expertise.isin(exp)]
fc = courses.copy()
if cat: fc=fc[fc.CourseCategory.isin(cat)]
if level: fc=fc[fc.CourseLevel.isin(level)]

a,b,c,d=st.columns(4)
a.metric("Avg Teacher Rating",f"{ft.TeacherRating.mean():.2f}")
b.metric("Avg Course Rating",f"{fc.CourseRating.mean():.2f}")
c.metric("Instructors",f"{len(ft):,}")
d.metric("Courses",f"{len(fc):,}")

st.subheader("Instructor Performance Leaderboard")
st.dataframe(
    leaderboard[leaderboard.TeacherID.isin(ft.TeacherID)][
        ["Rank","TeacherName","Expertise","YearsOfExperience","TeacherRating",
         "AverageCourseRating","Enrollments","PerformanceTier"]
    ],use_container_width=True,hide_index=True
)

x,y=st.columns(2)
with x:
    st.subheader("Experience vs Teacher Rating")
    fig=px.scatter(ft,x="YearsOfExperience",y="TeacherRating",color="Expertise",
                   hover_name="TeacherName",trendline="ols")
    st.plotly_chart(fig,use_container_width=True)
with y:
    st.subheader("Course Quality by Category")
    tmp=fc.groupby("CourseCategory",as_index=False).CourseRating.mean()
    fig=px.bar(tmp,x="CourseCategory",y="CourseRating",text_auto=".2f")
    st.plotly_chart(fig,use_container_width=True)

x,y=st.columns(2)
with x:
    st.subheader("Course Quality by Level")
    tmp=fc.groupby("CourseLevel",as_index=False).CourseRating.mean()
    fig=px.bar(tmp,x="CourseLevel",y="CourseRating",text_auto=".2f")
    st.plotly_chart(fig,use_container_width=True)
with y:
    st.subheader("Expertise-wise Performance")
    tmp=expertise[expertise.Expertise.isin(ft.Expertise.unique())]
    fig=px.bar(tmp.sort_values("AvgCourseRating"),x="AvgCourseRating",y="Expertise",
               orientation="h",text_auto=".2f")
    st.plotly_chart(fig,use_container_width=True)

st.subheader("Course Category × Level Heatmap")
heat=fc.pivot_table(index="CourseCategory",columns="CourseLevel",
                    values="CourseRating",aggfunc="mean")
fig=px.imshow(heat,text_auto=".2f",aspect="auto")
st.plotly_chart(fig,use_container_width=True)
