########1
# from manim import *

# class FractionIntroduction(Scene):
#     def construct(self):
#         # Create text to introduce fractions
#         title = Text("Learning Fractions").scale(0.9).to_edge(UP)
#         subtitle = Text("A fraction represents a part of a whole", color=BLUE).scale(0.7).next_to(title, DOWN)

#         # Add introduction text to the scene
#         self.play(Write(title))
#         self.play(FadeIn(subtitle))
#         self.wait(1)

#         # Introduce components of a fraction: numerator and denominator
#         fraction_text = Text("1/4", font_size=72)
#         numerator = Text("Numerator: 1, represents a part of the whole", font_size=36).next_to(fraction_text, UP)
#         denominator = Text("Denominator: 4, indicates the whole is divided into four equal parts", font_size=36).next_to(fraction_text, DOWN)

#         # Display the fraction and explanations
#         self.play(Write(fraction_text))
#         self.wait(1)
#         self.play(Write(numerator))
#         self.wait(1)
#         self.play(Write(denominator))
#         self.wait(2)

#         # Fade out all text before showing the graphical illustration
#         self.play(
#             FadeOut(title),
#             FadeOut(subtitle),
#             FadeOut(fraction_text),
#             FadeOut(numerator),
#             FadeOut(denominator)
#         )

#         # Use a graphic to illustrate the meaning of the fraction
#         circle = Circle(radius=2, color=GREEN)
#         partitions = VGroup(*[
#             Line(circle.get_center(), point, color=WHITE)
#             for point in circle.get_points_defining_boundary()[::len(circle.get_points_defining_boundary()) // 4]
#         ])
#         shaded_part = Sector(outer_radius=2, angle=PI/2, color=BLUE)

#         # Add circle and partition lines to the scene
#         self.play(Create(circle))
#         self.play(Create(partitions), run_time=2)
#         self.play(FadeIn(shaded_part), run_time=2)
#         self.wait(2)

#         # Summarize the meaning of the fraction
#         summary = Text("This blue section represents one quarter of the circle", font_size=36, color=BLUE).to_edge(DOWN)
#         self.play(Write(summary))
#         self.wait(3)

#         # Clear the scene - selectively fade out VMobjects
#         vmobjects = [obj for obj in self.mobjects if isinstance(obj, VMobject)]
#         self.play(FadeOut(VGroup(*vmobjects)))

# # The following is the command to run the animation
# if __name__ == "__main__":
#     scene = FractionIntroduction()
#     scene.render()



########2
# from manim import *

# class CompareFractionsScene(Scene):
#     def construct(self):
#         # Introduction and explanation of fractions
#         title = Text("Comparing Fractions").to_edge(UP)
#         explanation = Text("We will find a common denominator for 2/5 and 3/8",
#                            font_size=36).next_to(title, DOWN)

#         self.play(Write(title))
#         self.play(FadeIn(explanation))
#         self.wait(1)

#         # Show original fractions
#         fractions = VGroup(
#             Text("2/5", color=BLUE),
#             Text("3/8", color=GREEN)
#         ).arrange(RIGHT, buff=1)
#         fractions.move_to(UP * 0.5)

#         self.play(Write(fractions[0]), Write(fractions[1]))
#         self.wait(1)

#         # Explain LCD
#         lcd_explanation = Text("Finding the Least Common Denominator (LCD)", font_size=24)
#         lcd_explanation.to_edge(UP * 0.5)
#         self.play(Write(lcd_explanation))
#         self.wait(1)

#         # Calculate the LCD
#         lcd_calculation = Text("LCD of 5 and 8 is 40", color=YELLOW)
#         lcd_calculation.next_to(lcd_explanation, DOWN)
#         self.play(Write(lcd_calculation))
#         self.wait(2)

#         # Convert fractions to equivalent forms
#         conversions = VGroup(
#             Text("2/5 becomes 16/40", color=BLUE),
#             Text("3/8 becomes 15/40", color=GREEN)
#         ).arrange(DOWN, buff=0.5)
#         conversions.next_to(lcd_calculation, DOWN)

#         self.play(Write(conversions[0]), Write(conversions[1]))
#         self.wait(2)

#         # Visual representation of fractions
#         pies = VGroup(Circle(color=BLUE), Circle(color=GREEN)).arrange(RIGHT, buff=2)
#         pies.scale(0.5)
#         pies.next_to(conversions, DOWN)

#         # Divide the pies into sections
#         self.divide_pie(pies[0], 40, 16, BLUE)  # 2/5 converted to 16/40
#         self.divide_pie(pies[1], 40, 15, GREEN)  # 3/8 converted to 15/40

#         # Compare the sections
#         compare_text = Text("Blue pie has more sections colored, so 2/5 is greater than 3/8",
#                             font_size=24)
#         compare_text.next_to(pies, DOWN)
#         self.play(Write(compare_text))
#         self.wait(3)

#         # Cleanup
#         self.play(*[FadeOut(mob) for mob in self.mobjects])

#     def divide_pie(self, pie, total_parts, colored_parts, color):
#         # This function will visually divide the pie into equal parts
#         for i in range(total_parts):
#             angle = 2 * PI / total_parts
#             start_angle = i * angle
#             end_angle = start_angle + angle
#             sector = Sector(outer_radius=1, start_angle=start_angle,
#                             angle=angle, color=color if i < colored_parts else WHITE,
#                             fill_opacity=1 if i < colored_parts else 0.2)
#             sector.move_to(pie.get_center())
#             self.play(Create(sector), run_time=0.1)

# # To run the animation
# if __name__ == "__main__":
#     scene = CompareFractionsScene()
#     scene.render()

########3
from manim import *

class CompareFractionsScene(Scene):
    def construct(self):
        # Introduction and explanation of fractions
        title = Text("Comparing Fractions", font_size=36).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Fade out the title to declutter
        self.play(FadeOut(title))

        # Show original fractions in plain text
        fractions = VGroup(
            Text("1/2", color=BLUE),
            Text("2/5", color=GREEN)
        ).arrange(RIGHT, buff=1)
        fractions.move_to(UP * 1.5)

        self.play(Write(fractions[0]), Write(fractions[1]))
        self.wait(1)

        # Explain LCD in plain text
        lcd_explanation = Text("Finding the Least Common Denominator (LCD)", font_size=24)
        self.play(Write(lcd_explanation))
        self.wait(1)

        # Calculate the LCD
        lcd_calculation = Text("LCD of 2 and 5 is 10", color=YELLOW).next_to(lcd_explanation, DOWN)
        self.play(Write(lcd_calculation))
        self.wait(2)

        # Convert fractions to equivalent forms using plain text
        conversions = VGroup(
            Text("1/2 becomes 5/10", color=BLUE),
            Text("2/5 becomes 4/10", color=GREEN),
            Text("With LCD, we know which is bigger", color=RED)
        ).arrange(DOWN, buff=0.5)
        conversions.next_to(lcd_calculation, DOWN)

        self.play(Write(conversions[0]), Write(conversions[1]))
        self.wait(2)

        # # Clean up before showing pies
        # self.play(FadeOut(lcd_explanation), FadeOut(lcd_calculation), FadeOut(conversions))

        # # Visual representation of fractions using pies
        # pies = VGroup(Circle(color=BLUE), Circle(color=GREEN)).arrange(RIGHT, buff=2)
        # pies.scale(0.5)
        # pies.to_edge(DOWN)

        # # Divide the pies into sections
        # self.divide_pie(pies[0], 10, 5, BLUE)  # 1/2 converted to 5/10
        # self.divide_pie(pies[1], 10, 4, GREEN)  # 2/5 converted to 4/10

        # # Compare the sections
        # compare_text = Text("Blue pie has more sections colored, so 1/2 is greater than 2/5", font_size=24).next_to(pies, DOWN)
        # self.play(Write(compare_text))
        # self.wait(3)

        # # Callout the importance of finding the common denominator
        # callout_text = Text("Finding a common denominator is key to comparing fractions!", font_size=24, color=YELLOW).next_to(compare_text, DOWN)
        # self.play(Write(callout_text))
        # self.wait(3)

        # # Cleanup: Filter out non-VMobject types and then fade out
        # vmobjects = [obj for obj in self.mobjects if isinstance(obj, VMobject)]
        # self.play(FadeOut(VGroup(*vmobjects)))

    def divide_pie(self, pie, total_parts, colored_parts, color):
        # This function visually divides the pie into equal parts
        for i in range(total_parts):
            angle = 2 * PI / total_parts
            start_angle = i * angle
            sector = Sector(outer_radius=1, start_angle=start_angle,
                            angle=angle, color=color if i < colored_parts else WHITE,
                            fill_opacity=1 if i < colored_parts else 0.5)
            sector.move_to(pie.get_center())
            self.play(Create(sector), run_time=0.1)

# To run the animation
if __name__ == "__main__":
    scene = CompareFractionsScene()
    scene.render()
