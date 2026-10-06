<div class="<?php breevia_print_archive_entry_class('wp-block wp-block-kubio-query-loop-item  position-relative wp-block-kubio-query-loop-item__container breevia-index__k__QtetVXHJ9I-container breevia-local-364-container d-flex   '); ?>"" data-kubio="kubio/query-loop-item">
	<div class="position-relative wp-block-kubio-query-loop-item__inner breevia-index__k__QtetVXHJ9I-inner breevia-local-364-inner d-flex h-flex-basis h-px-lg-3 v-inner-lg-3 h-px-md-3 v-inner-md-3 h-px-3 v-inner-3">
		<div class="position-relative wp-block-kubio-query-loop-item__align breevia-index__k__QtetVXHJ9I-align breevia-local-364-align h-y-container h-column__content h-column__v-align flex-basis-100 align-self-lg-start align-self-md-start align-self-start">
			<figure class="wp-block wp-block-kubio-post-featured-image  position-relative wp-block-kubio-post-featured-image__container breevia-index__k__iE82N7AEu-container breevia-local-365-container kubio-post-featured-image--has-image h-aspect-ratio--16-9 <?php breevia_post_missing_featured_image_class(); ?>" data-kubio="kubio/post-featured-image" data-kubio-settings="{{kubio_settings_value}}">
				<?php if(has_post_thumbnail()): ?>
				<img class='position-relative wp-block-kubio-post-featured-image__image breevia-index__k__iE82N7AEu-image breevia-local--image' src='<?php echo esc_url(get_the_post_thumbnail_url());?>' />
				<?php endif; ?>
				<div class="position-relative wp-block-kubio-post-featured-image__inner breevia-index__k__iE82N7AEu-inner breevia-local-365-inner">
					<div class="position-relative wp-block-kubio-post-featured-image__align breevia-index__k__iE82N7AEu-align breevia-local-365-align h-y-container align-self-lg-center align-self-md-center align-self-center"></div>
				</div>
			</figure>
			<a class="position-relative wp-block-kubio-post-title__link breevia-index__k__tstzQ_uACq-link breevia-local-366-link d-block" href="<?php echo esc_url(get_the_permalink()); ?>">
				<h4 class="wp-block wp-block-kubio-post-title  position-relative wp-block-kubio-post-title__container breevia-index__k__tstzQ_uACq-container breevia-local-366-container" data-kubio="kubio/post-title">
					<?php the_title(); ?>
				</h4>
			</a>
			<div class="wp-block wp-block-kubio-divider  position-relative wp-block-kubio-divider__outer breevia-index__k__6a1i4GAlxkOt-outer breevia-local-367-outer" data-kubio="kubio/divider">
				<div class="position-relative wp-block-kubio-divider__width-container breevia-index__k__6a1i4GAlxkOt-width-container breevia-local-367-width-container">
					<div class="position-relative wp-block-kubio-divider__line breevia-index__k__6a1i4GAlxkOt-line breevia-local-367-line"></div>
				</div>
			</div>
			<p class="wp-block wp-block-kubio-post-excerpt  position-relative wp-block-kubio-post-excerpt__text breevia-index__k__-hWWlFyCEF-text breevia-local-368-text" data-kubio="kubio/post-excerpt">
				<?php breevia_post_excerpt(array (
  'max_length' => 16,
)); ?>
			</p>
			<div class="wp-block wp-block-kubio-post-meta  position-relative wp-block-kubio-post-meta__metaDataContainer breevia-index__k__in2mlwF4a-metaDataContainer breevia-local-369-metaDataContainer h-blog-meta" data-kubio="kubio/post-meta">
				<span class="metadata-item">
					<a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta("ID"))); ?>">
						<?php echo esc_html(get_the_author_meta("display_name",get_post_field("post_author"))); ?>
					</a>
				</span>
				<span class="metadata-separator">
					-
				</span>
				<span class="metadata-item">
					<a href="<?php echo esc_url(get_day_link(get_post_time( 'Y' ),get_post_time( 'm' ),get_post_time( 'j' ))); ?>">
						<?php echo esc_html(get_the_date('F j, Y')); ?>
					</a>
				</span>
			</div>
			<div class="position-relative wp-block-kubio-read-more-button__spacing breevia-index__k__7TrnS1SQ70-spacing breevia-local-370-spacing">
				<span class="wp-block wp-block-kubio-read-more-button  position-relative wp-block-kubio-read-more-button__outer breevia-index__k__7TrnS1SQ70-outer breevia-local-370-outer kubio-button-container" data-kubio="kubio/read-more-button">
					<a class="position-relative wp-block-kubio-read-more-button__link breevia-index__k__7TrnS1SQ70-link breevia-local-370-link h-w-100 h-global-transition" href="<?php echo esc_url(get_the_permalink()); ?>">
						<span class="h-svg-icon wp-block-kubio-read-more-button__icon breevia-index__k__7TrnS1SQ70-icon breevia-local-370-icon" name="icons8-line-awesome/long-arrow-right">
							<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="long-arrow-right" viewBox="0 0 512 545.5">
								<path d="M339 180.5l96 96 11.5 11.5-11.5 11.5-96 96-22.5-23L385 304H64v-32h321l-68.5-68.5z"/></svg>
							</span>
							<span class="position-relative wp-block-kubio-read-more-button__text breevia-index__k__7TrnS1SQ70-text breevia-local-370-text kubio-inherit-typography">
								<?php esc_html_e('Read more', 'breevia'); ?>
							</span>
						</a>
					</span>
				</div>
			</div>
		</div>
	</div>
