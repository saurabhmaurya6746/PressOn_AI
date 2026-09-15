import { PageIntro } from "@/components/ui/PageIntro";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { FinalCta } from "@/components/ui/FinalCta";
import { SEO } from "@/components/common/SEO";
import founderImage from "@/assets/images/founder-khushi.jpg";

export function About() {
  const philosophy = [
    ["01", "Personal", "Designed around you, never a template."],
    ["02", "Handcrafted", "Made carefully by hand, detail by detail."],
    ["03", "Elegant", "Refined finishes with timeless appeal."],
    ["04", "Expressive", "Nails that say something about your aura."],
  ] as const;

  return (
    <>
      <SEO
        title="Meet Khushi"
        description="Discover the passion, craftsmanship, and personal philosophy behind Aura Nails by Khushi."
      />

      <PageIntro eyebrow="Our story" title="Meet Khushi">
        The artist and heart behind Aura Nails—where creativity, craftsmanship, and
        personal expression meet.
      </PageIntro>

      {/* Founder Story */}
      <section className="py-24">
        <div className="section-shell grid items-center gap-14 lg:grid-cols-2">
          <div className="relative">
            <img
              src={founderImage}
              alt="Khushi, founder of Aura Nails"
              width={1008}
              height={1200}
              className="aspect-[4/5] w-full object-cover shadow-luxe"
            />
            <div className="absolute -bottom-6 -right-3 bg-lavender p-6 font-display text-2xl sm:right-8">
              Made with intention
            </div>
          </div>
          <div>
            <SectionHeading
              eyebrow="A passion in every detail"
              title="Artistry you can feel"
            />
            <div className="mt-7 space-y-5 leading-8 text-muted-foreground">
              <p>
                Aura Nails began with Khushi’s love for transforming small
                details into something deeply personal. Every extension,
                hand-painted accent, and custom press-on set is approached as
                wearable art.
              </p>
              <p>
                From understanding your style to perfecting the final finish, the
                experience is thoughtful, warm, and tailored to you. It is luxury
                without distance—beautiful craftsmanship made approachable.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Philosophy */}
      <section className="bg-blush/25 py-24">
        <div className="section-shell">
          <SectionHeading
            centered
            eyebrow="Our philosophy"
            title="The Aura Nails Philosophy"
          />
          <div className="mt-12 grid gap-5 md:grid-cols-4">
            {philosophy.map(([number, title, desc]) => (
              <article key={title} className="border-t border-primary p-6">
                <span className="text-xs font-semibold text-lavender-deep">
                  {number}
                </span>
                <h3 className="mt-8 font-display text-3xl">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  {desc}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <FinalCta />
    </>
  );
}
