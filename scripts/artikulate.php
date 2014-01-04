<?php
  $translation_file = "edu";
  include_once( "functions.inc" );
  $site_root = "../";
  $page_title = i18n_noop( "Artikulate Course Overview" );

  include ( "header.inc" );
?>

<?php echo i18n_var( 'Currently, the following resource files are available for Artikulate.' ); ?>

<?php include ( "artikulate_data.html" ); ?>

<hr width="30%" align="center" />
<p>
<?php echo i18n_var( 'Last update: %1', date ("Y-m-d", filemtime( "artikulate_data.html" ) ) ); ?>
</p>

  <?php

  include "footer.inc";
?>