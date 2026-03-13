/**
 * cleanup-empty-tag-scopes.ts
 *
 * Removes tag_scopes that have NO linked problems (neither regular nor mock)
 * from NeonDB, then removes any tags that become orphaned as a result.
 *
 * Usage:
 *   npx tsx scripts/data-management/cleanup-empty-tag-scopes.ts          # dry-run (safe preview)
 *   npx tsx scripts/data-management/cleanup-empty-tag-scopes.ts --delete  # execute deletion
 */

import { prisma } from '../../shared/lib/prisma';

async function cleanupEmptyTagScopes() {
    const isDeleteMode = process.argv.includes('--delete');

    console.log('─────────────────────────────────────────────────');
    console.log('🔍  Empty Tag Scope Cleanup');
    console.log(`🛠   Mode: ${isDeleteMode ? '⚠️  DELETE' : '👁  DRY RUN (pass --delete to execute)'}`);
    console.log('─────────────────────────────────────────────────\n');

    try {
        // ── Step 1: Find tag_scopes with zero linked problems (any type) ──────────
        const emptyTagScopes = await prisma.tag_scopes.findMany({
            where: {
                problemtags: { none: {} }   // no rows in problemtags for this scope
            },
            include: {
                tags: { select: { name: true, category: true } },
                sections: { select: { name: true } },
                examtypes: { select: { name: true } },
            }
        });

        console.log(`📊  Total tag_scopes with zero linked problems: ${emptyTagScopes.length}`);

        if (emptyTagScopes.length === 0) {
            console.log('\n✅  Database is already clean. Nothing to delete.');
            return;
        }

        // Print a preview table
        console.log('\n📋  Tag scopes that will be removed:\n');
        console.log('  #   Tag Name                              Category   Exam   Section');
        console.log('  ─── ───────────────────────────────────── ────────── ────── ──────────');
        emptyTagScopes.slice(0, 50).forEach((ts: any, i: number) => {
            const name = (ts.tags?.name || 'Unknown').padEnd(40);
            const cat  = (ts.tags?.category || '?').padEnd(10);
            const exam = (ts.examtypes?.name || '?').padEnd(6);
            const sec  = ts.sections?.name || '?';
            console.log(`  ${String(i + 1).padStart(3)} ${name} ${cat} ${exam} ${sec}`);
        });
        if (emptyTagScopes.length > 50) {
            console.log(`  ... and ${emptyTagScopes.length - 50} more`);
        }

        // ── Step 2: Find tags that would become orphaned after deletion ───────────
        const emptyTagScopeIds = emptyTagScopes.map((ts: any) => ts.tagScopeId);
        const tagIdsInEmptyScopes = [...new Set(emptyTagScopes.map((ts: any) => ts.tagid))];

        // A tag becomes orphaned if ALL of its tag_scopes are in our deletion set
        const orphanedTags = await prisma.tags.findMany({
            where: {
                tagid: { in: tagIdsInEmptyScopes },
                tag_scopes: { none: { tagScopeId: { notIn: emptyTagScopeIds } } }
            },
            select: { tagid: true, name: true, category: true }
        });

        console.log(`\n🏷   Tags that will be fully removed (all scopes empty): ${orphanedTags.length}`);
        orphanedTags.forEach((t: any) => {
            console.log(`     • [${t.category}] ${t.name}`);
        });

        if (!isDeleteMode) {
            console.log('\n─────────────────────────────────────────────────');
            console.log('⚠️   DRY RUN COMPLETE — no data was changed.');
            console.log('👉  Run with --delete to execute the cleanup.');
            console.log('─────────────────────────────────────────────────');
            return;
        }

        // ── Step 3: Execute deletions ─────────────────────────────────────────────
        console.log('\n🚀  Executing deletions...\n');

        // Delete empty tag_scopes (cascades to user_tag_performance if any)
        const deletedScopes = await prisma.tag_scopes.deleteMany({
            where: { tagScopeId: { in: emptyTagScopeIds } }
        });
        console.log(`✅  Deleted ${deletedScopes.count} empty tag_scope(s)`);

        // Delete orphaned tags (those with no remaining scopes)
        let deletedTags = { count: 0 };
        if (orphanedTags.length > 0) {
            deletedTags = await prisma.tags.deleteMany({
                where: {
                    tagid: { in: orphanedTags.map((t: any) => t.tagid) },
                    tag_scopes: { none: {} }    // safety check: still no scopes
                }
            });
            console.log(`✅  Deleted ${deletedTags.count} orphaned tag(s)`);
        }

        // ── Summary ───────────────────────────────────────────────────────────────
        console.log('\n─────────────────────────────────────────────────');
        console.log('🎉  Cleanup complete!');
        console.log(`    tag_scopes removed : ${deletedScopes.count}`);
        console.log(`    tags removed       : ${deletedTags.count}`);
        console.log('─────────────────────────────────────────────────');

    } catch (error) {
        console.error('\n❌  Error during cleanup:', error);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

cleanupEmptyTagScopes();
